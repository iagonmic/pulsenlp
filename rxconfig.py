import reflex as rx

config = rx.Config(
    app_name="nltk_sentimental_analysis",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)