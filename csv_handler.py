"""
Módulo de gestión de archivos CSV.
Lee facturas desde archivo CSV y las prepara para procesar.
"""

import csv
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from utils import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


class CSVHandler:
    """Gestiona la lectura de archivos CSV de facturas."""
    
    def __init__(self, archivo_csv: str = "facturas.csv"):
        """
        Inicializa el manejador de CSV.
        
        Args:
            archivo_csv: Ruta del archivo CSV
        """
        self.archivo_csv = Path(archivo_csv)
        self.datos = []
        
    def cargar_csv(self) -> bool:
        """
        Carga el archivo CSV.
        
        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            if not self.archivo_csv.exists():
                logger.error(f"Archivo {self.archivo_csv} no encontrado")
                return False
            
            self.datos = []
            
            with open(self.archivo_csv, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for idx, row in enumerate(reader, start=2):  # Empezar desde fila 2
                    # Mapear columnas CSV a estructura interna
                    fila = {
                        'numero_fila': idx,  # Para referencia
                        'fecha': row.get('FECHA', '').strip(),
                        'codigo': row.get('CODIGO', '').strip(),
                        'descripcion': row.get('PRODUCTO SERVICO:', '').strip(),
                        'monto': row.get('PRECIO UNITARIO', '').strip(),
                        'cuit_cliente': row.get('CUIT_CLIENTE', '99999999999').strip() or '99999999999',
                        'nombre_cliente': row.get('NOMBRE_CLIENTE', 'Consumidor Final').strip() or 'Consumidor Final',
                        'estado': row.get('ESTADO', 'PENDIENTE').strip() or 'PENDIENTE',
                        'cae': row.get('CAE', '').strip(),
                        'nro_comprobante': row.get('NRO_COMPROBANTE', '').strip()
                    }
                    
                    # Validar datos mínimos (solo PENDIENTE)
                    if fila['fecha'] and fila['descripcion'] and fila['monto'] and fila['estado'].upper() == 'PENDIENTE':
                        self.datos.append(fila)
                        logger.info(f"Fila {idx} cargada: {fila['descripcion']}")
                    else:
                        if fila['estado'].upper() != 'PENDIENTE':
                            logger.debug(f"Fila {idx} ignorada (estado={fila['estado']})")
                        else:
                            logger.warning(f"Fila {idx} ignorada por datos incompletos")
            
            logger.info(f"CSV cargado: {len(self.datos)} facturas válidas")
            return True
            
        except Exception as e:
            logger.error(f"Error al cargar CSV: {e}")
            return False
    
    def obtener_filas_pendientes(self) -> List[Dict]:
        """
        Obtiene todas las filas con estado = PENDIENTE.
        
        Returns:
            List[Dict]: Lista de diccionarios con los datos de cada fila
        """
        pendientes = [fila for fila in self.datos if fila['estado'].upper() == 'PENDIENTE']
        logger.info(f"Se encontraron {len(pendientes)} facturas pendientes")
        return pendientes
    
    def obtener_todas(self) -> List[Dict]:
        """
        Obtiene todas las filas sin filtrar.
        
        Returns:
            List[Dict]: Lista de todos los datos
        """
        return self.datos
    
    def actualizar_fila(self, numero_fila: int, cae: str, nro_comprobante: str) -> bool:
        """
        Actualiza una fila en memoria con el CAE y número de comprobante.
        Cambia el estado de PENDIENTE a PROCESADO.
        
        Args:
            numero_fila: Número de fila a actualizar
            cae: Código de Autorización Electrónica
            nro_comprobante: Número de comprobante
            
        Returns:
            bool: True si se actualizó exitosamente
        """
        try:
            for fila in self.datos:
                if fila['numero_fila'] == numero_fila:
                    fila['cae'] = cae
                    fila['nro_comprobante'] = nro_comprobante
                    fila['estado'] = "PROCESADO"
                    logger.info(f"Fila {numero_fila} actualizada: CAE={cae}, Nro={nro_comprobante}, Estado=PROCESADO")
                    return True
            
            logger.error(f"Fila {numero_fila} no encontrada")
            return False
            
        except Exception as e:
            logger.error(f"Error al actualizar fila {numero_fila}: {e}")
            return False
    
    def guardar_csv(self, archivo_salida: str = "facturas_emitidas.csv") -> bool:
        """
        Guarda los cambios en un nuevo CSV.
        
        Args:
            archivo_salida: Nombre del archivo de salida
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            logger.info(f"📝 Intentando guardar {len(self.datos)} filas en {archivo_salida}...")
            
            archivo_salida_path = Path(archivo_salida)
            
            with open(archivo_salida_path, 'w', newline='', encoding='utf-8-sig') as f:
                fieldnames = ['FECHA', 'CODIGO', 'PRODUCTO SERVICO:', 'PRECIO UNITARIO', 
                              'CUIT_CLIENTE', 'NOMBRE_CLIENTE', 'ESTADO', 'CAE', 'NRO_COMPROBANTE']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                
                filas_escritas = 0
                for fila in self.datos:
                    try:
                        writer.writerow({
                            'FECHA': fila['fecha'],
                            'CODIGO': fila['codigo'],
                            'PRODUCTO SERVICO:': fila['descripcion'],
                            'PRECIO UNITARIO': fila['monto'],
                            'CUIT_CLIENTE': fila['cuit_cliente'],
                            'NOMBRE_CLIENTE': fila['nombre_cliente'],
                            'ESTADO': fila['estado'],
                            'CAE': fila['cae'],
                            'NRO_COMPROBANTE': fila['nro_comprobante']
                        })
                        filas_escritas += 1
                    except Exception as e:
                        logger.error(f"  ✗ Error escribiendo fila: {e}")
                        continue
            
            logger.info(f"✓ CSV guardado: {archivo_salida_path} ({filas_escritas} filas)")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error al guardar CSV: {e}", exc_info=True)
            return False
