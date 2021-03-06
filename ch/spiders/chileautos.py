# -*- coding: utf-8 -*-
import scrapy

# Newer than 2014, more expensive than 10 million
# start_urls = ['http://www.chileautos.cl/cemagic.asp?region=0&ciudad=0&tipo=Todos&carroceria=&maresp=0&modelo=&combustible=0&kilom=&c_otros=&cili=0&cilf=0&vendedor=0&ai=2013&af=2017&pi=10000000&pf=1000000000&fecha_ini=&fecha_fin=&disp=1&dea=25&pag=1&boton=4']

# All of them... be careful with this request... maybe I'll be over quota
start_urls = ['http://www.chileautos.cl/cemagic.asp?region=0&ciudad=0&tipo=Todos&carroceria=&maresp=0&modelo=&combustible=0&kilom=&c_otros=&cili=0&cilf=0&vendedor=0&ai=1920&af=2017&pi=0&pf=1000000000&fecha_ini=&fecha_fin=&disp=1&dea=100&pag=1&boton=4']


class ChileAutosScrapper(scrapy.Spider):
    name = 'chileautosspider'
    start_urls = start_urls

    def parse(self, response):
        for auto in response.css('tr.des'):
            href = auto.css(':nth-child(2) a::attr(href)').extract_first()
            yield scrapy.Request(response.urljoin(href),
                                 callback=self.parse_auto)


        next_page = response.css('a.nav#sig ::attr(href)').extract_first()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page),
                                 callback=self.parse)

    def parse_auto(self, response):
        interesting_attrs = (
            ('Marca:', 'brand', 'str'),
            ('Modelo:', 'model', 'str'),
            ('Patente:', 'license_plate', 'str'),
            ('Versión:', 'submodel', 'str'),
            ('Año', 'year', 'int'),
            ('Tipo vehíc:', '_type', 'str'),
            ('Carrocería:', 'chasis', 'str'),
            ('Color:', 'color', 'str'),
            ('Kilometraje', 'mileage', 'str'),
            ('Cilindrada', 'engine_size', 'str'),
            ('Potencia', 'power', 'str'),
            ('Transmision', 'transmision', 'str'),
            ('Dirección', 'handling', 'str'),
            ('Aire', 'air', 'bool'),
            ('Radio', 'radio', 'str'),
            ('Alzavidrios', 'window', 'str'),
            ('Espejos', 'mirrors', 'str'),
            ('Frenos', 'brakes', 'str'),
            ('Airbag', 'airbags', 'bool'),
            ('Unico Dueño', 'unique_owner', 'bool'),
            ('Cierre', 'closing', 'str'),
            ('Catalítico', 'cathalitic', 'bool'),
            ('Combustible', 'fuel', 'str'),
            ('Llantas', 'rims', 'bool'),
            ('Puertas', 'doors', 'int'),
            ('Alarma', 'alarm', 'bool'),
            ('Portal', 'website', 'str'),
            ('Techo', 'roof', 'str'),
            ('Vende', 'seller', 'str'),
            ('Teléfono', 'phone_number', 'str'),
            ('Ciudad', 'city', 'str'))

        result = {}
        data = {}
        next_is_price = False
        for auto in response.css('table.tablaauto.justificado tr'):
            attr_name = get_attr_name(auto)
            attr_value = get_attr_value(auto, attr_name)

            if next_is_price: # this one is price
                data['Precio'] = attr_name
                next_is_price = False
                continue
            if attr_name == 'Precio': # next one will be price
                next_is_price = True

            # try to find one of the interesting attrs
            name_value = get_value_with_type(attr_name, attr_value, interesting_attrs)
            if name_value:
                name, value = name_value
                data[name] = value

        result['url'] = response.url
        result['main_image'] = response.css('img#imgp ::attr(src)').extract_first()
        result['data'] = data

        yield result

def get_attr_name(response):
    return response.css(':nth-child(1) ::text').extract_first().strip()


def get_attr_value(response, attr_name=''):
    attr_value = ''
    try:
        attr_value = response.css(':nth-child(2) ::text').extract_first().strip()
    except Exception:
        pass

    if attr_value == attr_name:
        try:
            attr_value = response.css('.quiebre ::text').extract_first().strip()
        except Exception:
            pass

    return attr_value


def get_value_with_type(source_attr_name, source_attr_value, interesting_attrs):
    for _attr_name_orig, _attr_name, _type in interesting_attrs:
        if source_attr_name == _attr_name_orig:
            return (_attr_name, by_type(source_attr_value, _type))



def by_type(value, _type):
    if _type == 'int':
        try:
            return int(value)
        except Exception:
            return value
    if _type == 'bool' and value is not None:
        return value.strip().lower() in ['si', 's', 'y', 'yes']

    return value


# i'm using following functions to debug scrapy locally
#
# def get_value(attr):
#     for auto in response.css('table.tablaauto.justificado tr'):
#         if auto.css(':nth-child(1) ::text').extract_first() == attr:
#             return auto

# def get_value2(attr):
#     for auto in response.css('table.tablaauto.justificado tr'):
#         if auto.css(':nth-child(1) ::text').extract_first().strip().startswith('<b>'):
#             return auto
