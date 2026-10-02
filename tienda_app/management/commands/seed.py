from django.core.management.base import BaseCommand

from tienda_app.models import Inventario, Libro


class Command(BaseCommand):
    help = "Carga datos de prueba (libros con inventario). Idempotente."

    def handle(self, *args, **options):
        datos = [
            ("Clean Code en Python", 150.0, 10),
            ("Harry Potter y La Orden del Fénix", 132.0, 10),
            ("Cien años de Soledad", 155.0, 10),
        ]
        for titulo, precio, stock in datos:
            libro, _ = Libro.objects.get_or_create(
                titulo=titulo, defaults={"precio": precio}
            )
            Inventario.objects.get_or_create(
                libro=libro, defaults={"cantidad": stock}
            )

        self.stdout.write(self.style.SUCCESS("Datos de prueba cargados."))
