class SourceDescriptor:
    def __get__(self, variable, owner):
        return variable.__dict__.get(self.name, list())

    def __set__(self, variable, sources):
        if isinstance(sources, SourceDescriptor):
            return
        if variable.track is not None:
            if variable.data_type == 'Folder' or variable.descends_from_list:
                raise ValueError
            for source in sources:
                if source not in variable.track.variables:
                    raise ValueError
        variable.__dict__[self.name] = sources

    def __set_name__(self, owner, name):
        self.name = name


class ParentDescriptor:
    def __get__(self, variable, owner):
        return variable.__dict__.get(self.name, '')

    def __set__(self, variable, parent):
        if isinstance(parent, ParentDescriptor):
            return
        if variable.track is not None:
            if parent not in variable.track.variables:
                raise ValueError
        variable.__dict__[self.name] = parent

    def __set_name__(self, owner, name):
        self.name = name
