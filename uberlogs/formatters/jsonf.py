import six
import maya
from .simple_jsonf import SimpleJsonFormatter
from time import mktime


class JsonFormatter(SimpleJsonFormatter):

    def __init__(self, max_length=100, **kwargs):
        super(JsonFormatter, self).__init__(**kwargs)
        self.max_length = max_length

    def _transform(self, value, then):
        if isinstance(value, maya.Datetime):
            value = maya.MayaDT(mktime(value.timetuple()))
        if isinstance(value, maya.MayaDT):
            value = value.iso8601()

        return then(str(value))

    def _truncate(self, value):
        if len(value) <= self.max_length:
            return value

        return "{}...".format(value[:self.max_length - 3])

    def _get_message_obj(self, record):
        msg_obj = super(JsonFormatter, self)._get_message_obj(record)

        if not self.uber_record(record) or not record.uber_extra:
            return msg_obj

        arguments = record.uber_extra

        if self.parse_text:
            msg_obj["message"] = msg_obj["message"].format(**arguments)

        arguments = {k: self._transform(v, then=self._truncate)
                     for k, v in six.iteritems(arguments)}

        if not self.include_keywords and record.uber_kws:
            arguments = {k: v for k, v in six.iteritems(arguments)
                         if k not in record.uber_kws}

        return dict(msg_obj, **arguments)
