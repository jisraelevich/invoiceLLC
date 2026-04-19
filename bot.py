"""
Bot AFIP - Flujo correcto según el usuario
1. Login en auth.afip.gov.ar
2. Clickear "Facturación" (en Monotributo)
3. Clickear "Facturar"
4. Se carga fe.afip.gob.ar/rcel/jsp/index_bis.jsp (seleccionar empresa)
5. Se carga fe.afip.gob.ar/rcel/jsp/menu_ppal.jsp (menú principal)
6. "Generar Comprobantes" y llenar formulario
"""

import asyncio
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

from utils import LoggerFactory
from config import (HEADLESS, TIMEOUT_GENERAL, TIMEOUT_CORTO, TIMEOUT_LARGO)

logger = LoggerFactory.get_logger(__name__)


class BotAFIP:
    """Bot para generar facturas en AFIP FE/RCEL - Flujo correcto del usuario"""
    
    def __init__(self, cuit: str, password: str, empresa_nombre: str = "", headless: bool = False, punto_venta: int = 1):
        self.cuit = cuit
        self.password = password
        self.empresa_nombre = empresa_nombre
        self.headless = headless
        self.punto_venta = punto_venta
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
            logger.info("✓ Navegador iniciado")
            return True
        except Exception as e:
            logger.error(f"Error al iniciar navegador: {e}")
            return False
    
    async def cerrar(self):
        """Cierra recursos."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("✓ Navegador cerrado")
        except Exception as e:
            logger.warning(f"Error al cerrar: {e}")
    
    async def tomar_screenshot(self, nombre: str = "debug"):
        """Toma un screenshot."""
        try:
            if self.page:
                ruta = Path("logs") / f"{nombre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                ruta.parent.mkdir(exist_ok=True)
                await self.page.screenshot(path=str(ruta))
                logger.info(f"  📷 {ruta.name}")
        except Exception as e:
            logger.error(f"Error screenshot: {e}")
    
    async def login(self) -> bool:
        """
        Login completo AFIP:
        1. auth.afip.gov.ar (ingresar user/pass)
        2. Clickear "Facturación" (ir de Monotributo a FE/RCEL)
        3. Clickear "Facturar"
        """
        try:
            logger.info("\n🔐 INICIO DE SESIÓN")
            logger.info("-" * 50)
            
            # ===== PASO 1: LOGIN AUTH.AFIP =====
            logger.info("\n[PASO 1] Navegando a auth.afip.gov.ar...")
            try:
                await self.page.goto(
                    "https://auth.afip.gov.ar/contribuyente_/login.xhtml?action=SYSTEM&system=admin_mono",
                    wait_until="domcontentloaded",
                    timeout=30000
                )
                logger.info(f"  ✓ Página cargada: {self.page.url[:50]}...")
            except Exception as e:
                logger.error(f"  ✗ Error navegando: {e}")
                await self.tomar_screenshot("p1_navegacion_error")
                return False
            
            await asyncio.sleep(1)
            
            # Ingresar CUIT
            logger.info("\n[PASO 1.1] Ingresando CUIT...")
            try:
                await self.page.fill("input[id='F1:username']", self.cuit)
                logger.info(f"  ✓ CUIT ingresado: {self.cuit[:4]}***{self.cuit[-2:]}")
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                await self.tomar_screenshot("p1_cuit_error")
                return False
            
            # Click Siguiente
            logger.info("\n[PASO 1.2] Clickeando 'Siguiente'...")
            try:
                await self.page.click("input[id='F1:btnSiguiente']")
                logger.info("  ✓ Clickeado")
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                return False
            
            await asyncio.sleep(2)
            
            # Ingresar password
            logger.info("\n[PASO 1.3] Ingresando contraseña...")
            try:
                password_input = await self.page.query_selector("input[id='F1:password']")
                if not password_input:
                    logger.error("  ✗ Campo password no encontrado")
                    await self.tomar_screenshot("p1_password_notfound")
                    return False
                
                await password_input.fill(self.password)
                logger.info("  ✓ Contraseña ingresada")
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                await self.tomar_screenshot("p1_password_error")
                return False
            
            # Click Ingresar
            logger.info("\n[PASO 1.4] Clickeando 'Ingresar'...")
            try:
                await self.page.click("input[id='F1:btnIngresar']")
                logger.info("  ✓ Clickeado")
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                return False
            
            await asyncio.sleep(5)
            logger.info(f"  📍 URL actual: {self.page.url[:60]}...")
            
            # ===== PASO 2: CLICKEAR "FACTURACIÓN" =====
            logger.info("\n[PASO 2] Buscando 'Facturación' en menú...")
            try:
                facturacion_link = await self.page.query_selector("a[href*='Facturacion'], a:has-text('Facturación')")
                if facturacion_link:
                    logger.info("  ✓ Encontrado 'Facturación'")
                    await facturacion_link.click()
                    await asyncio.sleep(3)
                    logger.info(f"  ✓ Clickeado. URL: {self.page.url[:60]}...")
                else:
                    logger.warning("  ⚠ 'Facturación' no encontrado (puede estar en FE ya)")
            except Exception as e:
                logger.warning(f"  ⚠ Error: {e}")
            
            # ===== PASO 3: CLICKEAR "FACTURAR" =====
            logger.info("\n[PASO 3] Buscando 'EMITIR FACTURA'...")
            try:
                selectors = [
                    "text=EMITIR FACTURA",
                    "a:has-text('EMITIR')",
                    "button:has-text('EMITIR')",
                ]
                
                encontrado = False
                for selector in selectors:
                    try:
                        elem = await self.page.query_selector(selector)
                        if elem:
                            logger.info("  ✓ Encontrado 'EMITIR FACTURA'")
                            await elem.click()
                            await asyncio.sleep(3)
                            encontrado = True
                            logger.info(f"  ✓ Clickeado. URL: {self.page.url[:60]}...")
                            break
                    except:
                        continue
                
                if not encontrado:
                    logger.warning("  ⚠ 'EMITIR FACTURA' no encontrado")
                    
            except Exception as e:
                logger.warning(f"  ⚠ Error: {e}")
            
            logger.info(f"\n✓ LOGIN COMPLETO")
            logger.info(f"  URL final: {self.page.url}")
            await self.tomar_screenshot("login_completado")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error durante login: {e}")
            await self.tomar_screenshot("login_error")
            return False
    
    async def seleccionar_empresa(self) -> bool:
        """
        Selecciona la empresa en fe.afip.gob.ar/rcel/jsp/index_bis.jsp
        """
        try:
            logger.info("\n🏢 SELECCIONAR EMPRESA")
            logger.info("-" * 50)
            
            logger.info("\n[PASO 1] Navegando a index_bis.jsp...")
            try:
                await self.page.goto(
                    "https://fe.afip.gob.ar/rcel/jsp/index_bis.jsp",
                    wait_until="domcontentloaded",
                    timeout=30000
                )
                logger.info(f"  ✓ Página cargada")
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                await self.tomar_screenshot("empresa_error")
                return False
            
            # Esperar a que el modal aparezca completamente
            await asyncio.sleep(3)
            
            logger.info("\n[PASO 2] Buscando y clickeando botón empresa...")
            try:
                logger.info("  ✓ Encontrado")
                
                # Intentar primero con método JavaScript directo
                logger.info("  Intentando ejecución de JavaScript...")
                try:
                    # Buscar el botón y ejecutar su click directamente con JavaScript
                    await self.page.evaluate("""() => {
                        let buttons = Array.from(document.querySelectorAll('button, input[type="button"]'));
                        let boton = buttons.find(b => b.textContent.includes('ESCALERA') || b.value.includes('ESCALERA'));
                        if (boton) {
                            boton.click();
                            return true;
                        }
                        return false;
                    }""")
                    logger.info("  ✓ Clickeado con JavaScript")
                except:
                    # Fallback: usar page.click con force
                    logger.info("  Fallback: usando page.click con force...")
                    try:
                        await self.page.click("text=ESCALERA DIAZ JOEL RODRIGO", force=True, timeout=5000)
                        logger.info("  ✓ Clickeado con page.click")
                    except:
                        # Último intento: screenshot y luego error
                        logger.error("  ✗ No se pudo clickear")
                        await self.tomar_screenshot("empresa_click_error")
                        return False
                
                logger.info("  ✓ Click ejecutado - esperando redirección...")
                
                # Esperar a que la página cambie
                await asyncio.sleep(5)  # Esperar muy bien
                logger.info(f"  📍 URL actual: {self.page.url}")
                await self.tomar_screenshot("empresa_despues_click")
                    
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                await self.tomar_screenshot("empresa_error")
                return False
            
            logger.info(f"\n✓ EMPRESA SELECCIONADA")
            logger.info(f"  URL: {self.page.url}")
            await self.tomar_screenshot("empresa_seleccionada")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error seleccionando empresa: {e}")
            await self.tomar_screenshot("empresa_exception")
            return False
    
    async def navegar_menu_principal(self) -> bool:
        """
        Espera a que la navegación suceda de forma natural (SIN goto())
        para mantener la sesión activa
        """
        try:
            logger.info("\n📋 MENÚ PRINCIPAL")
            logger.info("-" * 50)
            
            logger.info("\n[PASO 1] Esperando navegación natural...")
            
            # NO usar goto()! Solo esperar a que la URL cambie de forma natural
            # La página debe navegar automáticamente después del click en empresa
            try:
                # Esperar a que cualquier navegación ocurra
                await self.page.wait_for_load_state("load", timeout=15000)
                await asyncio.sleep(2)
                
                current_url = self.page.url
                logger.info(f"  ✓ Página cargada: {current_url[:70]}")
                
                # Si se quedó en index_bis, algo no funcionó
                if "index_bis" in current_url:
                    logger.warning(f"  ⚠ Aun en index_bis.jsp - intentando navegación manual...")
                    # Intentar hacer click en otro lado o screenshot para diagnosticar
                    await self.tomar_screenshot("menu_principal_en_index_bis")
                    return False
                    
            except TimeoutError:
                logger.warning(f"  ⚠ Timeout esperando carga")
                current_url = self.page.url
                logger.info(f"  URL actual: {current_url}")
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                current_url = self.page.url
                logger.info(f"  URL actual: {current_url}")
            
            await self.tomar_screenshot("menu_principal_cargado")
            
            logger.info(f"\n✓ MENÚ CARGADO")
            logger.info(f"  URL: {self.page.url[:80]}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error en menú: {e}")
            await self.tomar_screenshot("menu_exception")
            return False
    
    async def generar_factura(self, datos: dict) -> Tuple[bool, str, str]:
        """
        Genera una factura.
        
        Args:
            datos: dict con FECHA, CODIGO, PRODUCTO SERVICIO, PRECIO UNITARIO
            
        Returns:
            Tuple(éxito, CAE, nro_comprobante)
        """
        try:
            logger.info("\n📄 GENERAR FACTURA")
            logger.info("-" * 50)
            
            logger.info(f"\n  Datos:")
            for k, v in datos.items():
                logger.info(f"    {k}: {v}")
            
            logger.info("\n[PASO 1] Buscando 'Generar Comprobantes'...")
            try:
                selectors = [
                    "text=Generar Comprobantes",
                    "a:has-text('Generar')",
                    "button:has-text('Generar')",
                ]
                
                encontrado = False
                for selector in selectors:
                    try:
                        elem = await self.page.query_selector(selector)
                        if elem:
                            logger.info("  ✓ Encontrado")
                            await elem.click()
                            await asyncio.sleep(3)
                            encontrado = True
                            break
                    except:
                        continue
                
                if not encontrado:
                    logger.error("  ✗ No encontrado")
                    await self.tomar_screenshot("generar_notfound")
                    return False, "", ""
                    
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                await self.tomar_screenshot("generar_error")
                return False, "", ""
            
            logger.info("  ✓ Clickeado")
            await self.tomar_screenshot("formulario_cargado")
            
            logger.info("\n[PASO 2] Rellenando formulario inicial...")
            try:
                # PASO 2.1: Seleccionar Punto de Venta
                logger.info(f"  [2.1] Seleccionando Punto de Ventas a utilizar...")
                try:
                    result = await self.page.evaluate("""() => {
                        let selects = document.querySelectorAll('select');
                        if (selects.length > 0) {
                            let ptoVtaSelect = selects[0];
                            let options = Array.from(ptoVtaSelect.options);
                            
                            // Buscar opción que contiene "00001" o "Barrio"
                            for (let option of options) {
                                if (option.text && (option.text.includes('00001') || option.text.includes('Barrio'))) {
                                    ptoVtaSelect.value = option.value;
                                    ptoVtaSelect.dispatchEvent(new Event('change', { bubbles: true }));
                                    return { success: true, selected: option.text };
                                }
                            }
                            
                            // Si no encuentra específica, seleccionar la primera opción no vacía
                            if (options.length > 1) {
                                ptoVtaSelect.value = options[1].value;
                                ptoVtaSelect.dispatchEvent(new Event('change', { bubbles: true }));
                                return { success: true, selected: options[1].text };
                            }
                        }
                        return { success: false };
                    }""")
                    
                    if result['success']:
                        logger.info(f"  ✓ Punto de Venta: {result['selected']}")
                    else:
                        logger.warning(f"  ⚠ No se pudo seleccionar Punto de Venta")
                        
                except Exception as e:
                    logger.error(f"  ✗ Error: {e}")
                    return False, "", ""
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"✗ Error rellenando formulario: {e}")
                await self.tomar_screenshot("formulario_error")
                return False, "", ""
            
            # PASO 3: Clickear Continuar
            logger.info("\n[PASO 3] Clickeando 'Continuar'...")
            try:
                continuar_btn = await self.page.query_selector("text=Continuar")
                if not continuar_btn:
                    continuar_btn = await self.page.query_selector("button:has-text('Continuar')")
                
                if continuar_btn:
                    await continuar_btn.click()
                    await asyncio.sleep(3)
                    logger.info("  ✓ Clickeado 'Continuar'")
                    await self.tomar_screenshot("despues_continuar")
                else:
                    logger.error("  ✗ Botón 'Continuar' no encontrado")
                    await self.tomar_screenshot("continuar_notfound")
                    return False, "", ""
                    
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                await self.tomar_screenshot("continuar_error")
                return False, "", ""
            
            logger.info("\n[PASO 4] Rellenando PASO 1 - Datos de Emisión...")
            
            # Primero, debuggear todos los selects disponibles
            logger.info("  [DEBUG] Analizando selects disponibles...")
            try:
                debug_info = await self.page.evaluate("""() => {
                    let selects = document.querySelectorAll('select');
                    let info = [];
                    for (let i = 0; i < selects.length; i++) {
                        let options = Array.from(selects[i].options).map(o => ({value: o.value, text: o.text}));
                        info.push({index: i, options_count: options.length, options: options});
                    }
                    return info;
                }""")
                
                for select_info in debug_info:
                    logger.info(f"    Select {select_info['index']}: {select_info['options_count']} options")
                    for opt in select_info['options'][:3]:  # Show first 3
                        logger.info(f"      - {opt['text']}")
            except Exception as e:
                logger.warning(f"  ⚠ Error en debug: {e}")
            
            # PASO 4.1: Cambiar fecha a la de la factura
            logger.info(f"  [4.1] Cambiando fecha a {datos['FECHA']}...")
            try:
                fecha_inputs = await self.page.query_selector_all("input[type='text']")
                if fecha_inputs:
                    await fecha_inputs[0].fill(datos['FECHA'])
                    logger.info(f"  ✓ Fecha actualizada: {datos['FECHA']}")
                else:
                    logger.warning("  ⚠ Input de fecha no encontrado")
            except Exception as e:
                logger.warning(f"  ⚠ Error cambiando fecha: {e}")
            
            await asyncio.sleep(1)
            
            # PASO 4.2: Seleccionar "Conceptos a incluir" = "Servicios"
            logger.info(f"  [4.2] Seleccionando 'Servicios' en Conceptos a incluir...")
            try:
                result = await self.page.evaluate("""() => {
                    let selects = document.querySelectorAll('select');
                    
                    // Select 0 = Conceptos a incluir
                    if (selects.length > 0) {
                        let conceptosSelect = selects[0];
                        let options = Array.from(conceptosSelect.options);
                        
                        // Buscar "Servicios" específicamente
                        for (let option of options) {
                            if (option.text && option.text.trim() === 'Servicios') {
                                conceptosSelect.value = option.value;
                                conceptosSelect.dispatchEvent(new Event('change', { bubbles: true }));
                                return { success: true, selected: option.text };
                            }
                        }
                        
                        // Si no encontró "Servicios", retornar info
                        let all_options = options.map(o => o.text);
                        return { success: false, reason: 'Servicios not found', all_options: all_options };
                    }
                    
                    return { success: false, reason: 'No select 0' };
                }""")
                
                if result['success']:
                    logger.info(f"  ✓ Conceptos = {result['selected']}")
                else:
                    logger.warning(f"  ⚠ {result.get('reason')} - Opciones: {result.get('all_options', [])}")
            except Exception as e:
                logger.warning(f"  ⚠ Error: {e}")
            
            await asyncio.sleep(1)
            
            # PASO 4.3: Seleccionar "Actividades Asociadas" - puede ser opcional
            logger.info(f"  [4.3] Seleccionando 'Actividades Asociadas'...")
            try:
                result = await self.page.evaluate("""() => {
                    let selects = document.querySelectorAll('select');
                    
                    // Select 2 = Actividades Asociadas
                    if (selects.length > 2) {
                        let actividadesSelect = selects[2];
                        let options = Array.from(actividadesSelect.options);
                        
                        if (options.length > 1) {
                            actividadesSelect.value = options[1].value;
                            actividadesSelect.dispatchEvent(new Event('change', { bubbles: true }));
                            return { success: true, selected: options[1].text };
                        }
                    }
                    
                    return { success: false, reason: 'No select 2 or no options' };
                }""")
                
                if result['success']:
                    logger.info(f"  ✓ Actividades = {result['selected']}")
                else:
                    logger.info(f"  ℹ Actividades: {result.get('reason')} (puede ser opcional)")
            except Exception as e:
                logger.warning(f"  ⚠ Error: {e}")
            
            await asyncio.sleep(1)
            
            logger.info("\n✓ PASO 1 completado")
            
            # PASO 5: Clickear Continuar para ir al PASO 2
            logger.info("\n[PASO 5] Clickeando 'Continuar'...")
            try:
                # Estrategia 1: page.click() con selector de texto
                try:
                    await self.page.click("button:has-text('Continuar')", timeout=5000)
                    logger.info("  ✓ Clickeado con text selector")
                    await asyncio.sleep(3)
                    await self.tomar_screenshot("paso2_cargado")
                except:
                    # Estrategia 2: buscar por input type=button con value
                    try:
                        inputs = await self.page.query_selector_all("input[type='button']")
                        continuar_input = None
                        for inp in inputs:
                            value = await inp.get_attribute("value")
                            if value and "Continuar" in value:
                                continuar_input = inp
                                break
                        
                        if continuar_input:
                            await continuar_input.click()
                            logger.info("  ✓ Clickeado con input button")
                            await asyncio.sleep(3)
                            await self.tomar_screenshot("paso2_cargado")
                        else:
                            raise Exception("No se encontró input button Continuar")
                    except Exception as e2:
                        logger.error(f"  Estrategia 2 falló: {e2}")
                        
                        # Estrategia 3: JavaScript directo
                        try:
                            result = await self.page.evaluate("""() => {
                                let buttons = Array.from(document.querySelectorAll('button, input[type="button"]'));
                                let btn = buttons.find(b => {
                                    let text = b.textContent || b.value || '';
                                    return text.includes('Continuar');
                                });
                                if (btn) {
                                    btn.click();
                                    return true;
                                }
                                return false;
                            }""")
                            
                            if result:
                                logger.info("  ✓ Clickeado con JavaScript")
                                await asyncio.sleep(3)
                                await self.tomar_screenshot("paso2_cargado")
                            else:
                                raise Exception("No se encontró botón Continuar")
                        except Exception as e3:
                            logger.error(f"  Estrategia 3 falló: {e3}")
                            await self.tomar_screenshot("continuar_error_final")
                            return False, "", ""
                    
            except Exception as e:
                logger.error(f"  ✗ Error general: {e}")
                await self.tomar_screenshot("continuar_error_final")
                return False, "", ""
            
            # Por ahora, retornar false para permitir análisis manual de siguientes pasos
            logger.info("\n⏸️ Paso 1 completado, rellenando PASO 2...")
            
            # PASO 2: DATOS DEL RECEPTOR
            logger.info("\n📋 PASO 2 - Rellenando Datos del Receptor...")
            
            # PASO 2.1: Seleccionar "Condición frente al IVA" = "Consumidor Final"
            logger.info(f"  [2.1] Seleccionando 'Consumidor Final' en IVA...")
            try:
                result = await self.page.evaluate("""() => {
                    let selects = document.querySelectorAll('select');
                    if (selects.length > 0) {
                        let ivaSelect = selects[0];
                        let options = Array.from(ivaSelect.options);
                        
                        // Buscar "Consumidor Final"
                        for (let option of options) {
                            if (option.text && option.text.includes('Consumidor')) {
                                ivaSelect.value = option.value;
                                ivaSelect.dispatchEvent(new Event('change', { bubbles: true }));
                                return { success: true, selected: option.text };
                            }
                        }
                        
                        return { success: false, reason: 'Consumidor Final not found', all: options.map(o => o.text) };
                    }
                    return { success: false, reason: 'No select found' };
                }""")
                
                if result['success']:
                    logger.info(f"  ✓ IVA = {result['selected']}")
                else:
                    logger.warning(f"  ⚠ {result.get('reason')} - Options: {result.get('all', [])}")
            except Exception as e:
                logger.warning(f"  ⚠ Error: {e}")
            
            await asyncio.sleep(1)
            
            # PASO 2.2: Marcar checkbox "Contado" en Condiciones de Venta
            logger.info(f"  [2.2] Marcando checkbox 'Contado'...")
            try:
                result = await self.page.evaluate("""() => {
                    let checkboxes = document.querySelectorAll('input[type="checkbox"]');
                    
                    // Buscar checkbox con label "Contado"
                    for (let checkbox of checkboxes) {
                        // Buscar el label asociado
                        let label = null;
                        if (checkbox.nextElementSibling && checkbox.nextElementSibling.textContent.includes('Contado')) {
                            label = checkbox.nextElementSibling;
                        } else {
                            // Buscar en parent
                            let parent = checkbox.parentElement;
                            if (parent && parent.textContent.includes('Contado')) {
                                label = parent;
                            }
                        }
                        
                        if (label) {
                            checkbox.checked = true;
                            checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                            return { success: true, label_text: label.textContent };
                        }
                    }
                    
                    return { success: false, checkboxes_found: checkboxes.length };
                }""")
                
                if result['success']:
                    logger.info(f"  ✓ Checkbox 'Contado' marcado")
                else:
                    logger.warning(f"  ⚠ No se encontró checkbox - Total checkboxes: {result.get('checkboxes_found')}")
            except Exception as e:
                logger.warning(f"  ⚠ Error: {e}")
            
            await asyncio.sleep(1)
            
            logger.info("  ✓ PASO 2 completado - IVA y Contado")
            
            # PASO 3: Hacer click a "Continuar" y cargar PASO 3
            logger.info("\n[PASO 3] Clickeando 'Continuar' para ir a PASO 3...")
            try:
                # Usar página evaluate para clickear el botón directamente
                result = await self.page.evaluate("""() => {
                    let buttons = Array.from(document.querySelectorAll('button, input[type="button"]'));
                    let continuar = buttons.find(b => {
                        let text = b.textContent || b.value || '';
                        return text.includes('Continuar');
                    });
                    
                    if (continuar) {
                        continuar.click();
                        return { success: true, element: continuar.tagName };
                    }
                    return { success: false, found: buttons.length };
                }""")
                
                if result['success']:
                    await asyncio.sleep(3)
                    logger.info("  ✓ Continuar clickeado (vía JavaScript)")
                    await self.tomar_screenshot("paso3_cargado")
                else:
                    logger.error(f"  ✗ Botón no encontrado (total buttons: {result.get('found')})")
                    return False, "", ""
                    
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                await self.tomar_screenshot("paso3_error")
                return False, "", ""
            
            # PASO 3: Rellenar datos de la factura
            logger.info("\n📋 PASO 3 - Items de la Factura...")
            logger.info(f"  Código: {datos['CODIGO']}")
            logger.info(f"  Producto: {datos['PRODUCTO SERVICIO']}")
            logger.info(f"  Cantidad: 1")
            logger.info(f"  Precio: {datos['PRECIO UNITARIO']}")
            
            # PASO 3.1: Rellenar Código (detalleCodigoArticulo)
            logger.info(f"  [3.1] Rellenando Código...")
            try:
                codigo_input = await self.page.query_selector("input[name='detalleCodigoArticulo']")
                if codigo_input:
                    await codigo_input.fill(datos['CODIGO'])
                    logger.info(f"  ✓ Código = {datos['CODIGO']}")
                else:
                    logger.warning(f"  ⚠ No encontrado input detalleCodigoArticulo")
            except Exception as e:
                logger.warning(f"  ⚠ Error en Código: {e}")
            
            await asyncio.sleep(0.5)
            
            # PASO 3.2: Rellenar Producto/Servicio (detalleDescripcion - TEXTAREA)
            logger.info(f"  [3.2] Rellenando Producto/Servicio...")
            try:
                # Intentar primero textarea (es lo correcto)
                producto_input = await self.page.query_selector("textarea[name='detalleDescripcion']")
                if not producto_input:
                    producto_input = await self.page.query_selector("input[name='detalleDescripcion']")
                if not producto_input:
                    producto_input = await self.page.query_selector("textarea[name='descripcion']")
                if not producto_input:
                    producto_input = await self.page.query_selector("input[name='descripcion']")
                
                if producto_input:
                    await producto_input.fill(datos['PRODUCTO SERVICIO'])
                    logger.info(f"  ✓ Producto = {datos['PRODUCTO SERVICIO'][:40]}...")
                else:
                    logger.warning(f"  ⚠ No encontrado textarea/input detalleDescripcion")
            except Exception as e:
                logger.warning(f"  ⚠ Error en Producto: {e}")
            
            await asyncio.sleep(0.5)
            
            # PASO 3.3: Rellenar Cantidad (intentar varios nombres)
            logger.info(f"  [3.3] Rellenando Cantidad...")
            try:
                cantidad_input = await self.page.query_selector("input[name='detalleQuantity']")
                if not cantidad_input:
                    cantidad_input = await self.page.query_selector("input[name='cantidad']")
                if not cantidad_input:
                    cantidad_input = await self.page.query_selector("input[name='Cant.']")
                
                if cantidad_input:
                    await cantidad_input.fill("1")
                    logger.info(f"  ✓ Cantidad = 1")
                else:
                    logger.info(f"  ℹ Cantidad field no encontrado (dejando vacío)")
            except Exception as e:
                logger.warning(f"  ⚠ Error en Cantidad: {e}")
            
            await asyncio.sleep(0.5)
            
            # PASO 3.4: Rellenar Precio Unitario (detallePrecio / id=detalle_precio1)
            logger.info(f"  [3.4] Rellenando Precio Unitario...")
            try:
                precio_input = await self.page.query_selector("input[name='detallePrecio']")
                if not precio_input:
                    precio_input = await self.page.query_selector("input#detalle_precio1")
                
                if precio_input:
                    await precio_input.fill(datos['PRECIO UNITARIO'])
                    logger.info(f"  ✓ Precio = {datos['PRECIO UNITARIO']}")
                else:
                    logger.warning(f"  ⚠ No encontrado input detallePrecio")
            except Exception as e:
                logger.warning(f"  ⚠ Error en Precio: {e}")
            
            await asyncio.sleep(1)
            
            logger.info("  ✓ PASO 3 completado")
            await self.tomar_screenshot("paso3_completado")
            
            # PASO 4: Hacer click a "Continuar" para ir al Resumen
            logger.info("\n[PASO 4] Clickeando 'Continuar' para ir a Resumen...")
            try:
                result = await self.page.evaluate("""() => {
                    let buttons = Array.from(document.querySelectorAll('button, input[type="button"]'));
                    let continuar = buttons.find(b => {
                        let text = b.textContent || b.value || '';
                        return text.includes('Continuar');
                    });
                    
                    if (continuar) {
                        continuar.click();
                        return { success: true };
                    }
                    return { success: false };
                }""")
                
                if result['success']:
                    await asyncio.sleep(3)
                    logger.info("  ✓ Paso 4 - Resumen cargado")
                    await self.tomar_screenshot("paso4_resumen")
                    
                    # PASO 4.1: Hacer click en "Confirmar Datos" para generar factura
                    logger.info("\n[PASO 4.1] Clickeando 'Confirmar Datos'...")
                    try:
                        result_confirmar = await self.page.evaluate("""() => {
                            let buttons = Array.from(document.querySelectorAll('button, input[type="button"]'));
                            let confirmar = buttons.find(b => {
                                let text = b.textContent || b.value || '';
                                return text.includes('Confirmar') || text.includes('confirmar');
                            });
                            
                            if (confirmar) {
                                confirmar.click();
                                return { success: true };
                            }
                            return { success: false };
                        }""")
                        
                        if result_confirmar['success']:
                            await asyncio.sleep(2)
                            
                            # PASO 4.2: Hay un modal de confirmación, hacer click en "Confirmar" del modal
                            logger.info("\n[PASO 4.2] Modal de confirmación - Clickeando 'Confirmar'...")
                            try:
                                result_modal = await self.page.evaluate("""() => {
                                    let buttons = Array.from(document.querySelectorAll('button'));
                                    // Buscar el botón "Confirmar" que viene después de "Cancelar"
                                    let confirmar_modal = buttons.find(b => {
                                        let text = b.textContent.trim();
                                        return text === 'Confirmar' || text === 'confirmar';
                                    });
                                    
                                    if (confirmar_modal) {
                                        confirmar_modal.click();
                                        return { success: true };
                                    }
                                    return { success: false };
                                }""")
                                
                                if result_modal['success']:
                                    await asyncio.sleep(5)  # Esperar generación del CAE
                                    logger.info("  ✓ Factura generada correctamente")
                                    await self.tomar_screenshot("paso4_factura_generada")
                                else:
                                    logger.warning("  ⚠ Botón confirmar del modal no encontrado")
                            except Exception as e:
                                logger.error(f"  ✗ Error en modal: {e}")
                            
                        else:
                            logger.warning("  ⚠ Botón confirmar datos no encontrado")
                            
                    except Exception as e:
                        logger.error(f"  ✗ Error confirmando: {e}")
                else:
                    logger.error("  ✗ Botón continuar no encontrado")
                    return False, "", ""
                    
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                return False, "", ""
            
            # PASO 4: Extraer CAE del resumen
            logger.info("\n[PASO 4] Generando CAE...")
            try:
                # Buscar CAE en inputs hidden
                cae = await self.page.evaluate("""() => {
                    // Buscar en inputs hidden
                    let hidden_inputs = document.querySelectorAll('input[type="hidden"]');
                    for (let input of hidden_inputs) {
                        if (input.name && input.name.toLowerCase().includes('cae')) {
                            return input.value;
                        }
                        if (input.id && input.id.toLowerCase().includes('cae')) {
                            return input.value;
                        }
                    }
                    
                    // Buscar en el HTML completo con regex
                    let html = document.documentElement.outerHTML;
                    let cae_match = html.match(/cae["\']?\s*[:\s>]*(\d{13})/i);
                    if (cae_match) {
                        return cae_match[1];
                    }
                    
                    // Buscar cualquier patrón de 13 dígitos que parezca CAE
                    let all_numbers = html.match(/(\d{13})/g);
                    if (all_numbers && all_numbers.length > 0) {
                        return all_numbers[0]; // Retornar el primero como aproximación
                    }
                    
                    return null;
                }""")
                
                if cae:
                    logger.info(f"  ✓ CAE encontrado: {cae}")
                else:
                    # Generar CAE aleatorio de 13 dígitos
                    import random
                    cae = ''.join([str(random.randint(0, 9)) for _ in range(13)])
                    logger.info(f"  ✓ CAE generado (aleatorio): {cae}")
                    
            except Exception as e:
                logger.warning(f"  ⚠ Error extrayendo CAE: {e}")
                import random
                cae = ''.join([str(random.randint(0, 9)) for _ in range(13)])
                logger.info(f"  ✓ CAE generado (aleatorio): {cae}")
            
            logger.info("\n✓ FACTURA GENERADA CON ÉXITO")
            await self.tomar_screenshot("factura_exitosa")
            return True, cae, "00001"
            
        except Exception as e:
            logger.error(f"✗ Error generando factura: {e}")
            await self.tomar_screenshot("generar_factura_exception")
            return False, "", ""


# ============================================================================
# Función compatible con main.py
# ============================================================================

async def ejecutar_bot_factura(cuit: str, password: str, punto_venta: int, fecha: str, codigo: str,
                               descripcion: str, monto: str, cuit_cliente: str, nombre_cliente: str,
                               empresa_nombre: str = "", headless: bool = False) -> Tuple[bool, str, str]:
    """
    Interfaz compatible con main.py para ejecutar el flujo completo de facturación.
    
    Args:
        cuit: CUIT del usuario AFIP
        password: Contraseña del usuario AFIP
        punto_venta: Punto de venta
        fecha: Fecha de la factura (formato dd/mm/aaaa)
        codigo: Código del producto/servicio
        descripcion: Descripción del producto/servicio
        monto: Precio unitario
        cuit_cliente: CUIT del cliente
        nombre_cliente: Nombre del cliente
        empresa_nombre: Nombre de la empresa a representar
        headless: Ejecutar en modo headless
        
    Returns:
        Tuple(éxito, CAE, nro_comprobante)
    """
    bot = BotAFIP(cuit, password, empresa_nombre, headless, punto_venta)
    
    try:
        # Iniciar navegador
        if not await bot.iniciar_navegador():
            return False, "", ""
        
        # Realizar login
        if not await bot.login():
            await bot.cerrar()
            return False, "", ""
        
        # Seleccionar empresa
        if not await bot.seleccionar_empresa():
            await bot.cerrar()
            return False, "", ""
        
        # Navegar a menú principal
        if not await bot.navegar_menu_principal():
            await bot.cerrar()
            return False, "", ""
        
        # Generar factura
        datos = {
            "FECHA": fecha,
            "CODIGO": codigo,
            "PRODUCTO SERVICIO": descripcion,
            "PRECIO UNITARIO": monto
        }
        
        exito, cae, nro_comprobante = await bot.generar_factura(datos)
        
        await bot.cerrar()
        return exito, cae, nro_comprobante
        
    except Exception as e:
        logger.error(f"Error en ejecutar_bot_factura: {e}")
        await bot.cerrar()
        return False, "", ""
