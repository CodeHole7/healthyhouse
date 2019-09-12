import psycopg2
import logging
from datetime import date

logging.basicConfig(filename='./delete_unscaned_dosimeters_%s.log' % str(date.today()), filemode='w', format='%(name)s - %(levelname)s - %(message)s')
TABLE = 'catalogue_dosimeter'
LIMIT_MONTH = 1

try:
    connection = psycopg2.connect(user = "vagrant",
                                  password = "vagrant",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "radonmeters")
    
    cursor = connection.cursor()

    # Print PostgreSQL version
    cursor.execute("SELECT id, line_id, EXTRACT(DAY FROM(CURRENT_TIMESTAMP - created)) as Datedif FROM %s"%TABLE)

    records = cursor.fetchall()

    delete_ids = []

    for record in records:
      if(int(record[2]) > LIMIT_MONTH):
        delete_ids.append((record[0], record[1]))
    # delete 
    for idx in delete_ids:
      cursor.execute("DELETE FROM catalogue_dosimeter WHERE id = '%s';DELETE FROM order_line WHERE id = '%s';" % (idx[0], idx[1]))
      connection.commit()
      logging.info('deleted %s entry:' % delete_ids[idx][0])

    logging.info('deleted %s entries:' % len(delete_ids))


    #print("You are connected to - ", record,"\n")
except (Exception, psycopg2.Error) as error :

    logging.error("Error while connecting to PostgreSQL: %s" % error)
    
finally:

    #closing database connection.
    if(connection):
        cursor.close()
        connection.close()
        logging.info("PostgreSQL connection is closed")
    logging.shutdown()