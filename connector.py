import pymysql.cursors
import pymysql


def get_data(key_id, logger):
    try:
        connection = pymysql.connect(host='saas.verticall.com.ar',
                                     user='crmtelemercadoco',
                                     password='vo(PTk+9IK=T',
                                     db='crmtelemercadoco_bpm',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
    except Exception, e:
        logger.error("Get connection error: %s" % str(e))
    result = None

    try:
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM `eg_email_adjunto_api` WHERE id_email = %s" % str(key_id)
            cursor.execute(sql)
            result = cursor.fetchone()
        logger.debug(str(result))
    except Exception, e:
        logger.error("fetch error: %s" % str(e))

    finally:
        connection.close()
        return result