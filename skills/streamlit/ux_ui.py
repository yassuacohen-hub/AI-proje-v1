# Streamlit UX/UI Yeteneği

from skills.base import registry


@registry.register(
    name="inject_css",
    description="Streamlit sayfasına özel CSS kuralları enjekte eder."
)
def inject_css(css_rules: str) -> str:
    """Custom CSS kurallarını streamlit sayfasına enjekte et."""
    return f"<style>{css_rules}</style>"


@registry.register(
    name="optimize_theme",
    description="Streamlit tema ayarlarını optimize eder (dark/light, renk token'ları)."
)
def optimize_theme(theme_config: dict) -> dict:
    """Tema ayarlarını optimize et. Ana renk, arka plan ve kontrast ayarları ekler."""
    theme_config.setdefault("primaryColor", "#1f77b4")
    theme_config.setdefault("backgroundColor", "#ffffff")
    theme_config.setdefault("secondaryBackgroundColor", "#f0f2f6")
    theme_config.setdefault("textColor", "#000000")
    return theme_config


@registry.register(
    name="generate_grid_layout",
    description="Streamlit st.columns ile responsive grid layout oluşturur."
)
def generate_grid_layout(columns: int = 3, gap: str = "medium") -> str:
    """Verilen sütun sayısına göre responsive grid layout üretir."""
    return f"st.columns({columns}, gap='{gap}')"


@registry.register(
    name="apply_design_tokens",
    description="Tasarım token'larını CSS değişkenlerine dönüştürür ve uygular."
)
def apply_design_tokens(tokens: dict) -> str:
    """Tasarım token'larını (renk, punto, boşluk, yarıçap, gölge) CSS değişkenlerine dönüştürür."""
    css_vars = ":root {\n"
    for key, value in tokens.items():
        css_vars += f"  --{key}: {value};\n"
    css_vars += "}\n"
    return css_vars


@registry.register(
    name="generate_chart_config",
    description="Plotly/Altair grafik yapılandırması üretir (yüksek performans, responsive)."
)
def generate_chart_config(chart_type: str = "plotly", height: int = 400, responsive: bool = True) -> dict:
    """Grafik yapılandırması üretir: layout, responsive, renk paleti ayarları."""
    return {
        "type": chart_type,
        "height": height,
        "responsive": responsive,
        "color_palette": "viridis",
        "template": "plotly_white"
    }


@registry.register(
    name="fix_layout_padding",
    description="Streamlit container padding ve margin sorunlarını düzeltir."
)
def fix_layout_padding(container_width: int = 1200, padding: str = "2rem") -> str:
    """Container padding ve margin sorunlarını düzeltmek için CSS üretir."""
    return f"""
    <style>
        .stContainer {{
            max-width: {container_width}px;
            padding: {padding};
            margin: 0 auto;
        }}
    </style>
    """
