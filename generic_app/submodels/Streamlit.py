import os
from generic_app.generic_models.html_report import HTMLReport

class Streamlit(HTMLReport):
    """
    A class to represent a Streamlit HTML report.

    Inherits from HTMLReport to generate an HTML iframe for embedding a Streamlit app.
    """

    def get_html(self, user):
        """
        Generate the HTML iframe for embedding the Streamlit app.

        Parameters
        ----------
        user : object
            The user object, which may contain user-specific information.

        Returns
        -------
        str
            The HTML string containing the iframe to embed the Streamlit app.
        """
        return f"""<iframe
              src="{os.getenv("STREAMLIT_URL", "http://localhost:8501")}/?embed=true"
              style="width:100%;border:none;height:100%"
            ></iframe>"""
