"""
Módulo Playwright para interacción con el portal AFIP.
Encargado de: login, navegación, carga de facturas y obtención de CAE.
"""

import asyncio
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

from utils import LoggerFactory
from config import (
    HEADLESS, TIMEOUT_GENERAL, TIMEOUT_CORTO, TIMEOUT_LARGO,
    AFIP_URL_LOGIN, AFIP_URL_COMPROBANTES
)

logger = LoggerFactory.get_logger(__name__)


class BotAFIP:
    """Bot para gestionar facturas en el portal AFIP."""
    
    # URLs del portal AFIP - Sistema de Comprobantes en Línea
    URL_INICIO_MONOTRIBUTO = "https://auth.afip.gov.ar/contribuyente_/login.xhtml?action=SYSTEM&system=admin_mono"
    URL_LOGIN_CLAVE = "https://auth.afip.gov.ar/contribuyente_/login.xhtml?action=SYSTEM&system=admin_mono"
    URL_GENERAR_FACTURAS = "https://fe.afip.gob.ar/rcel/jsp/index_bis.jsp"
    URL_MENU_PRINCIPAL = "https://fe.afip.gob.ar/rcel/jsp/menu_ppal.jsp"
    URL_BUSCAR_PUNTOS_VENTA = "https://fe.afip.gob.ar/rcel/jsp/buscarPtosVtas.do"
    
    def __init__(self, cuit: str, password: str, punto_venta: int, empresa_nombre: str = "", headless: bool = False):
        """
        Inicializa el bot.
        
        Args:
            cuit: CUIT del usuario AFIP
            password: Contraseña/Clave Fiscal
            punto_venta: Número de punto de venta
            empresa_nombre: Nombre de la empresa (para seleccionar en dropdown)
            headless: Si True, ejecuta sin interfaz gráfica
        """
        self.cuit = cuit
        self.password = password
        self.punto_venta = punto_venta
        self.empresa_nombre = empresa_nombre
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def iniciar_navegador(self):
        """Inicia el navegador Playwright."""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            logger.info("Navegador iniciado correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al iniciar navegador: {e}")
            return False
    
    async def tomar_screenshot(self, nombre: str = "error"):
        """
        Toma un screenshot de la pantalla actual.
        
        Args:
            nombre: Nombre del archivo sin extensión
        """
        try:
            if self.page:
                ruta = Path("logs") / f"{nombre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await self.page.screenshot(path=str(ruta))
                logger.info(f"Screenshot guardado: {ruta}")
        except Exception as e:
            logger.error(f"Error al tomar screenshot: {e}")
    
    async def login(self) -> bool:
        """
        Realiza el login en AFIP usando Clave Fiscal (ARCA).
        Flujo: Rellenar CUIT → Siguiente → Rellenar Clave Fiscal → Confirmar
        
        Returns:
            bool: True si el login fue exitoso
        """
        try:
            logger.info("Iniciando login en AFIP (Clave Fiscal)...")
            
            # Navegar a página de login de ARCA
            await self.page.goto(self.URL_INICIO_MONOTRIBUTO, wait_until="networkidle", timeout=TIMEOUT_GENERAL)
            logger.info(f"Página cargada: {self.URL_INICIO_MONOTRIBUTO}")
            
            await asyncio.sleep(1)
            
            # PASO 1: Rellenar CUIT (aunque venga pre-rellenado, lo sobrescribimos)
            logger.info("Paso 1: Ingresando CUIT desde configuración...")
            try:
                cuit_input = await self.page.query_selector("input[id*='username'], input[name*='username'], input[id*='F1:username']")
                if cuit_input:
                    # Limpiar el campo primero
                    await cuit_input.evaluate("element => element.value = ''")
                    # Rellenar con el CUIT del .env
                    await cuit_input.fill(self.cuit)
                    logger.info(f"CUIT ingresado: {self.cuit}")
                else:
                    logger.error("No se encontró campo de CUIT")
                    await self.tomar_screenshot("login_error")
                    return False
            except Exception as e:
                logger.error(f"Error al ingresar CUIT: {e}")
                await self.tomar_screenshot("login_error")
                return False
            
            # PASO 2: Click en botón "Siguiente"
            logger.info("Paso 2: Haciendo click en 'Siguiente'...")
            try:
                # Usar múltiples selectores como fallback
                selectors = [
                    "button:visible:has-text('Siguiente')",
                    "button[type='submit']:visible",
                    "text=Siguiente",
                ]
                
                clicked = False
                for selector in selectors:
                    try:
                        await self.page.click(selector, timeout=5000)
                        logger.info(f"Click en 'Siguiente' realizado con selector: {selector}")
                        clicked = True
                        break
                    except:
                        continue
                
                if not clicked:
                    logger.error("No se pudo clickear el botón 'Siguiente' con ningún selector")
                    await self.tomar_screenshot("login_error")
                    return False
                    
            except Exception as e:
                logger.error(f"Error al hacer click en 'Siguiente': {e}")
                await self.tomar_screenshot("login_error")
                return False
            
            await asyncio.sleep(2)
            
            # PASO 3: Ingresar Clave Fiscal (password)
            logger.info("Paso 3: Ingresando Clave Fiscal...")
            try:
                # Esperar a que cargue la página con el campo de password
                await self.page.wait_for_load_state("networkidle", timeout=TIMEOUT_GENERAL)
                
                # Buscar el campo de password - intentar múltiples selectores
                password_input = None
                selectors_password = [
                    "input[type='password']",
                    "input[name*='password'], input[name*='clave']",
                    "input[id*='password'], input[id*='clave']"
                ]
                
                for sel in selectors_password:
                    try:
                        await self.page.wait_for_selector(sel, timeout=5000)
                        password_input = await self.page.query_selector(sel)
                        if password_input:
                            break
                    except:
                        continue
                
                if password_input:
                    await password_input.fill(self.password)
                    logger.info("Clave Fiscal ingresada")
                else:
                    logger.error("No se encontró campo de Clave Fiscal")
                    await self.tomar_screenshot("login_error")
                    return False
            except Exception as e:
                logger.error(f"Error al ingresar Clave Fiscal: {e}")
                await self.tomar_screenshot("login_error")
                return False
            
            # PASO 4: Click en botón de confirmar
            logger.info("Paso 4: Confirmando Clave Fiscal...")
            try:
                # Intentar múltiples selectores para el botón
                selectors_botones = [
                    "button:visible",  # Buscar cualquier botón visible
                    "button[type='submit']",
                    "input[type='submit']",
                    "text=Ingresar",
                    "text=Confirmar"
                ]
                
                clicked = False
                for selector in selectors_botones:
                    try:
                        await self.page.click(selector, timeout=3000)
                        logger.info(f"Click realizado con selector: {selector}")
                        clicked = True
                        break
                    except:
                        continue
                
                if not clicked:
                    logger.warning("No se pudo clickear botón, intentando presionar Enter...")
                    await self.page.press("input[type='password']", "Enter")
                    logger.info("Enter presionado")
                    
            except Exception as e:
                logger.error(f"Error al confirmar: {e}")
                await self.tomar_screenshot("login_error")
                return False
            
            await asyncio.sleep(3)
            
            logger.info("Login completado exitosamente")
            return True
                
        except Exception as e:
            logger.error(f"Error durante login: {e}")
            await self.tomar_screenshot("login_error")
            return False
    
    async def navegar_a_comprobantes(self) -> bool:
        """
        Navega al flujo correcto de AFIP para generar comprobantes.
        Flujo real: menu_ppal.jsp → Generar comprobantes → Seleccionar punto venta → Continuar
        
        Returns:
            bool: True si se navegó exitosamente
        """
        try:
            logger.info("Navegando a menu principal de comprobantes...")
            
            # Navegar directamente a menu_ppal.jsp
            await self.page.goto(self.URL_MENU_PRINCIPAL, wait_until="networkidle")
            await asyncio.sleep(2)
            
            # Clickear "Generar comprobantes"
            logger.info("Buscando botón 'Generar comprobantes'...")
            
            generar_selectors = [
                "text=Generar comprobantes",
                "text=GENERAR COMPROBANTES",
                "a:has-text('Generar comprobantes')",
                "button:has-text('Generar comprobantes')",
            ]
            
            generar_clicked = False
            for selector in generar_selectors:
                try:
                    await self.page.click(selector, timeout=5000)
                    logger.info(f"Clickeado 'Generar comprobantes'")
                    generar_clicked = True
                    break
                except:
                    continue
            
            if not generar_clicked:
                logger.error("No se pudo clickear 'Generar comprobantes'")
                await self.tomar_screenshot("navegacion_error")
                return False
            
            await asyncio.sleep(2)
            await self.page.wait_for_load_state("networkidle", timeout=TIMEOUT_GENERAL)
            
            # Seleccionar punto de venta (única opción disponible)
            logger.info(f"Seleccionando punto de venta: {self.punto_venta}...")
            try:
                selects = await self.page.query_selector_all("select")
                
                if selects:
                    for select in selects:
                        try:
                            await select.select_option(str(self.punto_venta))
                            logger.info(f"Punto de venta {self.punto_venta} seleccionado")
                            break
                        except:
                            continue
                else:
                    logger.warning("No se encontraron selects de punto de venta, continuando...")
            except Exception as e:
                logger.warning(f"Error seleccionando punto de venta: {e}")
            
            await asyncio.sleep(1)
            
            # Clickear CONTINUAR
            logger.info("Clickeando CONTINUAR...")
            continuar_selectors = [
                "text=CONTINUAR",
                "text=Continuar",
                "button:has-text('CONTINUAR')",
                "button:has-text('Continuar')",
                "input[value='CONTINUAR']",
            ]
            
            continuar_clicked = False
            for selector in continuar_selectors:
                try:
                    await self.page.click(selector, timeout=5000)
                    logger.info(f"Clickeado CONTINUAR")
                    continuar_clicked = True
                    break
                except:
                    continue
            
            if not continuar_clicked:
                logger.warning("No se pudo clickear CONTINUAR")
            
            await asyncio.sleep(2)
            await self.page.wait_for_load_state("networkidle", timeout=TIMEOUT_GENERAL)
            
            logger.info("Navegación a comprobantes completada")
            return True
            
        except Exception as e:
            logger.error(f"Error al navegar a comprobantes: {e}")
            await self.tomar_screenshot("navegacion_error")
            return False
    
    async def generar_factura(self, fecha: str, codigo: str, descripcion: str, monto: str, 
                              cuit_cliente: str, nombre_cliente: str) -> Tuple[bool, str, str]:
        """
        Genera una factura en AFIP siguiendo el flujo exacto del portal.
        
        Args:
            fecha: Fecha en formato dd/mm/aaaa
            codigo: Código del producto/servicio (ej: 055)
            descripcion: Descripción del servicio
            monto: Monto total (sin separadores)
            cuit_cliente: CUIT o 99999999999 para Consumidor Final
            nombre_cliente: Nombre o razón social del cliente
            
        Returns:
            Tuple: (éxito, CAE, número_comprobante)
        """
        try:
            logger.info(f"Generando factura: {descripcion} - ${monto}")
            
            # Paso 1: Seleccionar tipo de comprobante (FACTURA C)
            await self._seleccionar_tipo_comprobante()
            
            # Paso 2: Continuar
            await self._clickear_continuar()
            
            # Paso 3: Ingresar fecha del comprobante
            await self._ingresar_fecha(fecha)
            
            # Paso 4: Concepto (SERVICIOS)
            await self._seleccionar_concepto()
            
            # Paso 5: Fechas desde/hasta y vencimiento
            await self._ingresar_fechas(fecha)
            
            # Paso 6: Continuar
            await self._clickear_continuar()
            
            # Paso 7: Condición frente al IVA (CONSUMIDOR FINAL)
            await self._seleccionar_condicion_iva()
            
            # Paso 8: Condiciones de venta (CONTADO)
            await self._seleccionar_condiciones_venta()
            
            # Paso 9: Continuar
            await self._clickear_continuar()
            
            # Paso 10: Código del producto/servicio
            await self._ingresar_codigo_producto(codigo)
            
            # Paso 11: Producto/Servicio y Precio
            await self._ingresar_descripcion_monto(descripcion, monto)
            
            # Paso 12: Continuar
            await self._clickear_continuar()
            
            # Paso 13: Confirmar datos
            await self._clickear_confirmar_datos()
            
            # Paso 14: Confirmar en popup
            await self._confirmar_popup()
            
            # Paso 15: Obtener CAE y número de comprobante
            cae, nro_comprobante = await self._extraer_cae_y_numero()
            
            if cae and nro_comprobante:
                logger.info(f"Factura generada exitosamente: CAE={cae}, Nro={nro_comprobante}")
                return True, cae, nro_comprobante
            else:
                logger.error("No se pudo obtener CAE o número de comprobante")
                await self.tomar_screenshot("factura_error")
                return False, "", ""
                
        except Exception as e:
            logger.error(f"Error al generar factura: {e}")
            await self.tomar_screenshot("factura_exception")
            return False, "", ""
    
    async def _clickear_continuar(self):
        """Clickea el botón CONTINUAR."""
        try:
            await self.page.click("button:has-text('CONTINUAR'), input[value='CONTINUAR']")
            logger.info("Botón CONTINUAR clickeado")
            await self.page.wait_for_load_state("networkidle", timeout=TIMEOUT_GENERAL)
        except Exception as e:
            logger.error(f"Error al clickear CONTINUAR: {e}")
            raise
    
    async def _seleccionar_tipo_comprobante(self):
        """Selecciona Factura C como tipo de comprobante."""
        try:
            # Buscar radio button o select para FACTURA C
            await self.page.wait_for_selector("input[type='radio'][value='C'], input[type='radio'][name*='comprobante']", timeout=TIMEOUT_CORTO)
            
            # Clickear FACTURA C
            elementos = await self.page.query_selector_all("input[type='radio']")
            for elemento in elementos:
                value = await elemento.get_attribute("value")
                if value and "C" in value.upper():
                    await elemento.click()
                    logger.info("Tipo de comprobante: FACTURA C seleccionado")
                    return
            
            logger.warning("No se encontró radio button de Factura C, intentando click directo")
            await self.page.click("input[value='C']")
            logger.info("Factura C seleccionada")
        except Exception as e:
            logger.error(f"Error al seleccionar tipo de comprobante: {e}")
            raise
    
    async def _seleccionar_punto_venta(self):
        """Selecciona el punto de venta."""
        try:
            # Buscar select de punto de venta
            await self.page.wait_for_selector("select[name*='punto'], select[id*='pto']", timeout=TIMEOUT_CORTO)
            
            # Seleccionar el punto de venta
            selects = await self.page.query_selector_all("select")
            for select in selects:
                options_text = await self.page.eval_on_selector("select", "el => Array.from(el.options).map(o => o.text)")
                if any(str(self.punto_venta) in text for text in options_text):
                    await select.select_option(str(self.punto_venta))
                    logger.info(f"Punto de venta {self.punto_venta} seleccionado")
                    return
            
            logger.warning("No se encontró select de punto de venta")
        except Exception as e:
            logger.error(f"Error al seleccionar punto de venta: {e}")
            raise
    
    async def _seleccionar_concepto(self):
        """Selecciona SERVICIOS como concepto."""
        try:
            # Buscar radio button o select para SERVICIOS
            await self.page.wait_for_selector("input[type='radio'][value*='3'], input[type='radio'][name*='concepto']", timeout=TIMEOUT_CORTO)
            
            elementos = await self.page.query_selector_all("input[type='radio']")
            for elemento in elementos:
                value = await elemento.get_attribute("value")
                label_text = await elemento.evaluate("el => el.parentElement?.textContent || ''")
                
                if "servicios" in label_text.lower() or (value and value == "3"):
                    await elemento.click()
                    logger.info("Concepto: SERVICIOS seleccionado")
                    return
            
            logger.warning("No se encontró opción SERVICIOS")
        except Exception as e:
            logger.error(f"Error al seleccionar concepto: {e}")
            raise
    
    async def _ingresar_fecha(self, fecha: str):
        """Ingresa la fecha del comprobante en formato dd/mm/aaaa."""
        try:
            # Buscar campo de fecha
            inputs_fecha = await self.page.query_selector_all("input[type='text'], input[name*='fecha'], input[placeholder*='fecha']")
            
            if inputs_fecha:
                await inputs_fecha[0].fill(fecha)
                logger.info(f"Fecha ingresada: {fecha}")
            else:
                logger.warning("No se encontró campo de fecha")
        except Exception as e:
            logger.error(f"Error al ingresar fecha: {e}")
            raise
    
    async def _ingresar_fechas(self, fecha_comprobante: str):
        """Ingresa fechas desde, hasta y vencimiento."""
        try:
            # Fecha desde (igual a la del comprobante)
            inputs = await self.page.query_selector_all("input[type='text']")
            
            if len(inputs) >= 2:
                await inputs[0].fill(fecha_comprobante)
                logger.info(f"Fecha DESDE ingresada: {fecha_comprobante}")
                
                # Fecha hasta (hoy)
                from datetime import datetime
                hoy = datetime.now().strftime("%d/%m/%Y")
                await inputs[1].fill(hoy)
                logger.info(f"Fecha HASTA ingresada: {hoy}")
            
            # Vencimiento (30 días después)
            if len(inputs) >= 3:
                from datetime import datetime, timedelta
                vto = (datetime.strptime(fecha_comprobante, "%d/%m/%Y") + timedelta(days=30)).strftime("%d/%m/%Y")
                await inputs[2].fill(vto)
                logger.info(f"Vencimiento ingresado: {vto}")
        except Exception as e:
            logger.error(f"Error al ingresar fechas: {e}")
            raise
    
    async def _seleccionar_condicion_iva(self):
        """Selecciona CONSUMIDOR FINAL como condición frente al IVA."""
        try:
            # Buscar radio button para CONSUMIDOR FINAL
            elementos = await self.page.query_selector_all("input[type='radio']")
            for elemento in elementos:
                label_text = await elemento.evaluate("el => el.parentElement?.textContent || el.nextElementSibling?.textContent || ''")
                
                if "consumidor final" in label_text.lower():
                    await elemento.click()
                    logger.info("Condición IVA: CONSUMIDOR FINAL seleccionada")
                    return
            
            logger.warning("No se encontró CONSUMIDOR FINAL")
        except Exception as e:
            logger.error(f"Error al seleccionar condición IVA: {e}")
            raise
    
    async def _seleccionar_condiciones_venta(self):
        """Selecciona CONTADO como condición de venta."""
        try:
            elementos = await self.page.query_selector_all("input[type='radio']")
            for elemento in elementos:
                label_text = await elemento.evaluate("el => el.parentElement?.textContent || el.nextElementSibling?.textContent || ''")
                
                if "contado" in label_text.lower():
                    await elemento.click()
                    logger.info("Condición de venta: CONTADO seleccionada")
                    return
            
            logger.warning("No se encontró CONTADO")
        except Exception as e:
            logger.error(f"Error al seleccionar condición de venta: {e}")
            raise
    
    async def _ingresar_codigo_producto(self, codigo: str = "055"):
        """Ingresa código para producto/servicio.
        
        Args:
            codigo: Código del producto/servicio (por defecto 055)
        """
        try:
            inputs = await self.page.query_selector_all("input[type='text']")
            if inputs:
                await inputs[0].fill(codigo)
                logger.info(f"Código producto ingresado: {codigo}")
        except Exception as e:
            logger.error(f"Error al ingresar código: {e}")
            raise
    
    async def _ingresar_descripcion_monto(self, descripcion: str, monto: str):
        """Ingresa descripción y monto del producto/servicio."""
        try:
            inputs = await self.page.query_selector_all("input[type='text'], textarea")
            
            # Descripción
            for inp in inputs:
                placeholder = await inp.get_attribute("placeholder")
                name = await inp.get_attribute("name")
                
                if placeholder and "producto" in placeholder.lower():
                    await inp.fill(descripcion)
                    logger.info(f"Descripción ingresada: {descripcion}")
                    break
            
            # Monto (precio unitario)
            for inp in inputs:
                placeholder = await inp.get_attribute("placeholder")
                if placeholder and ("precio" in placeholder.lower() or "monto" in placeholder.lower()):
                    await inp.fill(monto)
                    logger.info(f"Monto ingresado: ${monto}")
                    break
        except Exception as e:
            logger.error(f"Error al ingresar descripción/monto: {e}")
            raise
    
    async def _clickear_confirmar_datos(self):
        """Clickea botón para confirmar los datos antes del popup."""
        try:
            await self.page.click("button:has-text('CONFIRMAR'), input[value='CONFIRMAR']")
            logger.info("Datos confirmados")
            await self.page.wait_for_load_state("networkidle", timeout=TIMEOUT_GENERAL)
        except Exception as e:
            logger.error(f"Error al confirmar datos: {e}")
            raise
    
    async def _confirmar_popup(self):
        """Confirma el popup '¿Confirma la Operación?'"""
        try:
            # Esperar a que aparezca el popup
            await self.page.wait_for_selector("button:has-text('CONFIRMAR'), button:has-text('Sí'), input[value='CONFIRMAR']", timeout=TIMEOUT_CORTO)
            
            # Clickear CONFIRMAR en el popup
            await self.page.click("button:has-text('CONFIRMAR'), button:has-text('Sí'), input[value='CONFIRMAR']")
            logger.info("Popup de confirmación aceptado")
            
            # Esperar a que se procese
            await self.page.wait_for_load_state("networkidle", timeout=TIMEOUT_LARGO)
        except Exception as e:
            logger.error(f"Error al confirmar popup: {e}")
            raise
    
    async def _extraer_cae_y_numero(self) -> Tuple[str, str]:
        """
        Extrae el CAE y número de comprobante de la página de éxito.
        
        Returns:
            Tuple: (CAE, número_comprobante)
        """
        try:
            import re
            
            # Obtener el contenido de la página
            html = await self.page.content()
            
            # Buscar patrones de CAE (11 dígitos)
            cae_match = re.search(r'\b\d{11}\b', html)
            cae = cae_match.group() if cae_match else ""
            
            # Buscar número de comprobante (8 dígitos)
            nro_match = re.search(r'Comprobante.*?(\d{8})', html, re.IGNORECASE)
            nro_comprobante = nro_match.group(1) if nro_match else ""
            
            if not nro_comprobante:
                # Intentar patrón alternativo
                nro_match = re.search(r'(\d{8})', html)
                if nro_match:
                    nro_comprobante = nro_match.group(1)
            
            logger.info(f"CAE extraído: {cae}, Número: {nro_comprobante}")
            return cae, nro_comprobante
        except Exception as e:
            logger.error(f"Error al extraer CAE y número: {e}")
            return "", ""
    
    async def cerrar(self):
        """Cierra el navegador y limpia recursos."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("Navegador cerrado")
        except Exception as e:
            logger.error(f"Error al cerrar navegador: {e}")


async def ejecutar_bot_factura(cuit: str, password: str, punto_venta: int, 
                                fecha: str, codigo: str, descripcion: str, monto: str,
                                cuit_cliente: str, nombre_cliente: str,
                                empresa_nombre: str = "", headless: bool = False) -> Tuple[bool, str, str]:
    """
    Función auxiliar para ejecutar el bot de forma sincrónica.
    
    Returns:
        Tuple: (éxito, CAE, número_comprobante)
    """
    bot = BotAFIP(cuit, password, punto_venta, empresa_nombre, headless)
    
    try:
        if not await bot.iniciar_navegador():
            return False, "", ""
        
        if not await bot.login():
            return False, "", ""
        
        if not await bot.navegar_a_comprobantes():
            return False, "", ""
        
        return await bot.generar_factura(fecha, codigo, descripcion, monto, cuit_cliente, nombre_cliente)
    finally:
        await bot.cerrar()
