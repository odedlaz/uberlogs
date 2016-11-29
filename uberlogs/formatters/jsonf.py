import six

from .simple_jsonf import SimpleJsonFormatter


class JsonFormatter(SimpleJsonFormatter):

    @profile
    def _get_message_obj(self, record):
        msg_obj = super(JsonFormatter, self)._get_message_obj(record)

        if not self.uber_record(record) or not record.uber_extra:
            return msg_obj

        arguments = record.uber_extra

        if self.parse_text:
            msg_obj["message"] = msg_obj["message"].format(**arguments)

        if not self.include_keywords and record.uber_kws:
            arguments = {k: v for k, v in six.iteritems(arguments)
                         if k not in record.uber_kws}

        return dict(msg_obj, **arguments)
