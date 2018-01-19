from marshmallow_jsonapi import Schema, fields

field_map = {
        'string': fields.String,
        'integer': fields.Integer,
        'number': fields.Integer,
        'date-time': fields.DateTime,
        'boolean': fields.Boolean,
        'time': fields.Time,
        'formatted_string': fields.FormattedString,
        'float': fields.Float,
        'local_date_time': fields.LocalDateTime,
        'date': fields.Date,
        'url': fields.Url,
        'email': fields.Email,
        'function': fields.Function,
        'array': fields.List,
        'object': fields.Relationship,
        }

def dasherize(text):
    return text.replace('_', '-')

class ResourceSchemaFactory:
    def create_schema(resource_name, schemas):

        class ResourceSchema(Schema):
            id = fields.String()

            class Meta:
                type_ = resource_name
                inflect = dasherize

        resource_schema = ResourceSchema()
        for name, des in schemas['properties'].items():
            field_type = des['type']
            field_obj = None
            # print('n, d:', name, des)
            if field_type == 'array' or 'array' in field_type:
                sub_type = des['items']['type']
                if sub_type == 'object':
                    field_obj = fields.Relationship(type_=name)
                else:
                    field_obj = field_map['array'](
                       field_map[sub_type]
                        )
                # print(field_obj)
            elif field_type == 'object':
                if 'properties' in des:
                    rname = name
                    if 'meta' in des and\
                            'jsonapitype' in des['meta']:
                        rname = des['meta']['jsonapitype']

                    sub_schema = ResourceSchemaFactory.create_schema(
                            rname,
                            des)
                    field_obj = fields.Relationship(type_=rname,
                                                    schema=sub_schema)
                else:
                    field_obj = fields.Relationship(type_=name)
            elif 'format' in des and des['format'] == 'date-time':
                field_obj = field_map['date-time']()
            else:
                field_obj = field_map[field_type]()

            if name in schemas['required']:
                field_obj.required = True

            resource_schema.fields[name] = field_obj
            resource_schema.declared_fields[name] = field_obj

        return resource_schema
