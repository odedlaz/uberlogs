import six

from .simple_jsonf import SimpleJsonFormatter


class JsonFormatter(SimpleJsonFormatter):

    @profile
    def _get_message_obj(self, record):
        msg_obj = super(JsonFormatter, self)._get_message_obj(record)
        if not self.uber_record(record):
            return msg_obj

        arguments = record.uber_extra

        message = record.getMessage()

        if self.parse_text:
            message = message.format(**arguments)

        msg_obj["message"] = message

        include_keywords = self.include_format_keywords

        if not self.parse_text:
            include_keywords = True

        if not include_keywords:
            arguments = {k: v for k, v in six.iteritems(arguments)
                         if k not in record.uber_kws}

        return dict(msg_obj, **arguments)
