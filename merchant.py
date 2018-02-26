class Merchant(object):
    """the class exposes various functions for a merchant to enable simple front end operations such as displaying merchant data"""

    def __init__(self):
        pass

    def user_merchants(self,primary_email):
        # retrieves a list of merchants that user has in their wallet / account
        pass

    def merchant_info(self,merchant_id):
        # retrives a list of merchant brand information for use by an app or website
        # use where a single request is required.  For multiple brands at once utilise merchant_group_info
        import sqlite3
        conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
        c = conn.cursor()

        c.execute("select merchant_id, merchant_nm, merchant_url, merchant_logo_url from merchants where merchant_id = ?", [merchant_id])

        return(c.fetchone())

    def merchant_group_info(self, merchant_id):
        # retrives a list of merchant brand information for use by an app or website
        # use where a list of merchants with associated details is required.  For single merchant requets utilise merchant_info
        import sqlite3
        conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
        c = conn.cursor()

        c.execute(
            "select merchant_id, merchant_nm, merchant_url, merchant_logo_url from merchants where merchant_id in ?",
            [merchant_id])

        return (c.fetchone())