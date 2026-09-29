# Streamlit UX/UI YeteneÄŸi

from skills.base import registry


@registry.register(
    name="inject_css",
    description="Streamlit sayfasÄ±na Ã¶zel CSS kurallarÄ± enjekte eder."
)
def inject_css(css_rules: str) -> str:
    """Custom CSS kurallarÄ±nÄ± streamlit sayfasÄ±na enjekte et."""
    return f"<style>{css_rules}</style>"


@registry.register(
    name="optimize_theme",
    description="Streamlit tema ayarlarÄ±nÄ± optimize eder (dark/light, renk token'larÄ±)."
)
def optimize_theme(theme_config: dict) -> dict:
    """Tema ayarlarÄ±nÄ± optimize et. Ana renk, arka plan ve kontrast ayarlarÄ± ekler."""
    theme_config.setdefault("primaryColor", "#1f77b4")
    theme_config.setdefault("backgroundColor", "#ffffff")
    theme_config.setdefault("secondaryBackgroundColor", "#f0f2f6")
    theme_config.setdefault("textColor", "#000000")
    return theme_config


@registry.register(
    name="generate_grid_layout",
    description="Streamlit st.columns ile responsive grid layout oluÅŸturur."
)
def generate_grid_layout(columns: int = 3, gap: str = "medium") -> str:
    """Verilen sÃ¼tun sayÄ±sÄ±na gÃ¶re responsive grid layout Ã¼retir."""
    return f"st.columns({columns}, gap='{gap}')"


@registry.register(
    name="apply_design_tokens",
    description="TasarÄ±m token'larÄ±nÄ± CSS deÄŸiÅŸkenlerine dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r ve uygular."
)
def apply_design_tokens(tokens: dict) -> str:
    """TasarÄ±m token'larÄ±nÄ± (renk, punto, boÅŸluk, yarÄ±Ã§ap, gÃ¶lge) CSS deÄŸiÅŸkenlerine dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r."""
    css_vars = ":root {\n"
    for key, value in tokens.items():
        css_vars += f"  --{key}: {value};\n"
    css_vars += "}\n"
    return css_vars


@registry.register(
    name="generate_chart_config",
    description="Plotly/Altair grafik yapÄ±landÄ±rmasÄ± Ã¼retir (yÃ¼ksek performans, responsive)."
)
def generate_chart_config(chart_type: str = "plotly", height: int = 400, responsive: bool = True) -> dict:
    """Grafik yapÄ±landÄ±rmasÄ± Ã¼retir: layout, responsive, renk paleti ayarlarÄ±."""
    return {
        "type": chart_type,
        "height": height,
        "responsive": responsive,
        "color_palette": "viridis",
        "template": "plotly_white"
    }


@registry.register(
    name="fix_layout_padding",
    description="Streamlit container padding ve margin sorunlarÄ±nÄ± dÃ¼zeltir."
)
def fix_layout_padding(container_width: int = 1200, padding: str = "2rem") -> str:
    """Container padding ve margin sorunlarÄ±nÄ± dÃ¼zeltmek iÃ§in CSS Ã¼retir."""
    return f"""
    <style>
        .stContainer {{
            max-width: {container_width}px;
            padding: {padding};
            margin: 0 auto;
        }}
    </style>
    """
