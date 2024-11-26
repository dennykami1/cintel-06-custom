# cintel-06-custom
plan and implement a custom project that includes interactive analytics and/or continuous intelligence

												
.venv\Scripts\activate
shiny run --reload --launch-browser dash/app.py
shiny static-assets remove
shinylive export dash docs