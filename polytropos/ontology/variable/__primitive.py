import logging
import re
from abc import abstractmethod
from collections import deque
from datetime import datetime
from typing import Optional, Any, cast, Set, List, Iterator, Deque
from urllib.parse import quote

from polytropos.ontology.variable import Variable

class Primitive(Variable):
    @classmethod
    @abstractmethod
    def cast(cls, value: Optional[Any]) -> Optional[Any]:
        pass

    @classmethod
    def sanitize(cls, value: Optional[Any]) -> Optional[Any]:
        """Where relevant, performs cleaning steps that, e.g., remove dangerous characters from values."""
        return value

    @classmethod
    def display_format(cls, value: Optional[Any]) -> str:
        """Returns a string representation of the value that's optimized for human reading."""
        if value is None:
            return ""

        return str(value)

class Integer(Primitive):
    @classmethod
    def cast(cls, value: Optional[Any]) -> Optional[int]:
        if value is None or value == "":
            return None
        return int(value)

    @classmethod
    def display_format(cls, value: Optional[int]) -> str:
        if value is None:
            return ""

        return "{:,}".format(value)

class Text(Primitive):
    @classmethod
    def cast(cls, value: Optional[Any]) -> Optional[str]:
        if value is None or value == "":
            return None
        return str(value)

    @classmethod
    def sanitize(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        s: str = cast(str, value)

        s_clean = s.lower() \
            .replace(".", "-") \
            .replace(",", "-") \
            .replace("'", "") \
            .replace('"', '') \
            .replace("&", "and") \
            .replace("#", "") \
            .replace(":", "-") \
            .replace(";", "-") \
            .replace(" ", "-") \
            .replace("_", "-") \
            .replace("/", "-") \
            .replace("(", "") \
            .replace(")", "")

        s_clean = re.sub('-+', '-', s_clean)
        s_clean = re.sub("^-+", "", s_clean)
        s_clean = re.sub("-+$", "", s_clean)

        return quote(s_clean)

class Decimal(Primitive):
    @classmethod
    def cast(cls, value: Optional[Any]) -> Optional[float]:
        if value is None or value == "":
            return None
        return float(value)

    @classmethod
    def display_format(cls, value: Optional[float]) -> str:
        if value is None:
            return ""

        return "{:,.02f}".format(value)

class Ratio(Decimal):
    @classmethod
    def display_format(cls, value: Optional[float]) -> str:
        if value is None:
            return ""

        return "{:,.0f}%".format(value*100)

class Unary(Primitive):
    @classmethod
    def cast(cls, value: Optional[Any]) -> Optional[bool]:
        if value is None or value == "":
            return None
        if value is True:
            return True
        if not (isinstance(value, str) and value.lower() == "x"):
            raise ValueError
        return True

    @classmethod
    def display_format(cls, value: Optional[Any]) -> str:
        if value is None:
            return ""

        assert value is True
        return "True"

class Binary(Primitive):
    @classmethod
    def cast(cls, value: Optional[Any]) -> Optional[bool]:
        if value is None or value == "":
            return None
        if isinstance(value, bool):
            return value
        vl = value.lower()
        if vl in {"1", "true"}:
            return True
        if vl in {"0", "false"}:
            return False
        raise ValueError

    @classmethod
    def display_format(cls, value: Optional[Any]) -> str:
        if value is None:
            return ""

        if value is True:
            return "Yes"
        elif value is False:
            return "No"
        else:
            raise ValueError("Unrecognized binary value {:}".format(value))

class Currency(Primitive):
    @classmethod
    def cast(cls, value: Optional[Any]) -> Optional[float]:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except ValueError:
            as_currency: int = int(float(value))
            logging.debug("Encountered fractional currency value (%s). Rounding down to nearest dollar (%s).", value,
                          as_currency)

            return as_currency

    @classmethod
    def display_format(cls, value: Optional[int]) -> str:
        if value is None:
            return ""

        if value < 0:
            return "-${:,}".format(abs(value))

        return "${:,}".format(value)

class Phone(Primitive):
    @classmethod
    def cast(cls, value: Optional[Any]) -> Optional[str]:
        if value is None or value == "":
            return None
        return str(value)

    @classmethod
    def display_format(cls, value: Optional[str]) -> str:
        if value is None:
            return ""

        if len(value) != 10 or not value.isnumeric():
            return value

        clean: str = "+1 (%s) %s-%s" % (value[0:3], value[3:6], value[6:10])
        return clean

class Email(Primitive):
    @classmethod
    def cast(cls, value: Optional[Any]) -> Optional[str]:
        if value is None or value == "":
            return None
        return str(value)

    @classmethod
    def display_format(cls, value: Optional[Any]) -> str:
        if value is None:
            return ""

        if value.count("@") != 1:
            return value

        value = value.strip()
        if re.match(r'[^@]+@[^@]+\.[^@]+', value) is None:
            return value

        if bool(re.search(r'[^-A-Za-z0-9@_.]', value)):
            return value

        value = value.lower()
        return '<a href="mailto:' + value + '">' + value + '</a>'

_common_tlds: Set[str] = {".org", ".com", ".edu", ".gov", ".mil", ".us", ".net", ".info", ".uk", ".eu", ".ca", ".au",
                          ".il"}

def _has_common_tld(url: str) -> bool:
    for tld in _common_tlds:
        if tld in url:
            return True
    return False

class URL(Primitive):
    link_template: str = '<a href="{:}" target="_blank" rel="ugc">{:}</a>'
    @classmethod
    def cast(cls, value: Optional[Any]) -> Optional[str]:
        if value is None or value == "":
            return None
        return str(value)

    @classmethod
    def display_format(cls, value: Optional[str]) -> str:
        if value is None:
            return ""

        urls: Iterator[str] = (url.strip() for url in re.split('[;,]', value))
        links: Deque[str] = deque()
        for url in urls:
            if not re.match("^[-A-Za-z0-9+&:#/%?=~_,.]*$", url):
                links.append(url)
                continue

            url = url.lower()

            if url in {"n/a", "na", "none", "", "na"}:
                continue

            if not _has_common_tld(url):
                links.append(url)  # Include the text of the URL but don't link it
                continue

            if not url.startswith("http"):
                url = "http://" + url

            url = url.replace("http//", "http://")
            url = url.replace("https//", "https://")
            link: str = cls.link_template.format(url, url)
            links.append(link)

        links_list: List[str] = list(links)

        if len(links_list) == 0:
            return ""

        return ", ".join(links_list)

class Date(Primitive):
    @classmethod
    def cast(cls, value: Optional[Any]) -> Optional[str]:
        if value is None or value in {"", "000000"}:
            return None
        if len(value) == 6 and value.isdecimal():
            year: str = value[:4]
            month: str = value[4:]
            return "%s-%s-01" % (year, month)

        if len(value) >= 10:
            retained = value[:10]

            # Will raise a ValueError if unexpected content
            datetime.strptime(retained, "%Y-%m-%d")

            return retained

        raise ValueError

class EIN(Primitive):

    @classmethod
    def cast(cls, value: Optional[Any]) -> Optional[str]:
        if value is None or value == "":
            return None

        return str(value)

    @classmethod
    def sanitize(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = str(value).strip().replace("-", "")

        if len(value) == 8 and value.isnumeric():
            logging.warning("Padding 8-digit EIN '%s' with a zero" % value)
            return "0" + value

        return value

    @classmethod
    def display_format(cls, value: Optional[str]) -> str:
        if value is None:
            return ""

        sanitized: str = cast(str, cls.sanitize(value))
        if len(sanitized) != 9 or not sanitized.isnumeric():
            return ""

        return "{:}-{:}".format(sanitized[0:2], sanitized[2:9])
