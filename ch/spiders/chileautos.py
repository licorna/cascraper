# -*- coding: utf-8 -*-
import scrapy


class ChileAutosScrapper(scrapy.Spider):
    name = 'chileautosspider'
    start_urls = ['http://www.chileautos.cl/cemagic.asp?region=0&ciudad=0&tipo=Todos&carroceria=&maresp=0&modelo=&combustible=0&kilom=&c_otros=&cili=0&cilf=0&vendedor=0&ai=2013&af=2017&pi=10000000&pf=1000000000&fecha_ini=&fecha_fin=&disp=1&dea=25&pag=1&boton=4']

    def parse(self, response):
        for auto in response.css('tr.des'):
            href = auto.css(':nth-child(2) a::attr(href)').extract_first()
            yield scrapy.Request(response.urljoin(href),
                                 callback=self.parse_auto)

        # next_page = response.css('a.nav#sig ::attr(href)').extract_first()
        # if next_page:
        #     yield scrapy.Request(response.urljoin(next_page),
                                 # callback=self.parse)

    def parse_auto(self, response):
        interesting_attrs = ('Marca:', 'Modelo:', 'Patente:', 'Versión:', 'Año:',
                             'Tipo vehíc:', 'Carrocería:', 'Color', 'Kilometraje',
                             'Cilindrada', 'Potencia', 'Transmisión', 'Dirección',
                             'Aire', 'Radio', 'Alzavidrios', 'Espejos', 'Frenos',
                             'Airbag', 'Unico Dueño', 'Cierre', 'Catalítico',
                             'Combustible', 'Llantas', 'Puertas', 'Alarma',
                             'Portal', 'Techo', 'Vende', 'Teléfono', 'Ciudad')

        data = {}
        next_is_price = False
        for auto in response.css('table.tablaauto.justificado tr'):
            attr_name = auto.css(':nth-child(1) ::text').extract_first().strip()

            try:
                attr_value = auto.css(':nth-child(2) ::text').extract_first().strip()
            except Exception:
                pass

            if next_is_price: # this one is price
                data['Precio'] = attr_name
                next_is_price = False
                continue
            if attr_name == 'Precio': # next one will be price
                next_is_price = True

            # try to find one of the interesting attrs
            for attr in interesting_attrs:
                if attr == attr_name:
                    data[attr] = attr_value

        yield data


def get_value(attr):
    for auto in response.css('table.tablaauto.justificado tr'):
        if auto.css(':nth-child(1) ::text').extract_first() == attr:
            return auto

def get_value2(attr):
    for auto in response.css('table.tablaauto.justificado tr'):
        if auto.css(':nth-child(1) ::text').extract_first().strip().startswith('<b>'):
            return auto
