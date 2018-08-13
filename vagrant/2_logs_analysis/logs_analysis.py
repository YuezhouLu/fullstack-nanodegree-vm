import psycopg2
import os
import time

DBNAME = "news"

def top_3_articles():
    """Return the title and the associated reviewed number of the top 3 most reviewed articles"""
    db = psycopg2.connect(database = DBNAME)
    c = db.cursor()
    query = '''select path, count(*) as article_views
                from log
                where path like '/article/%'
                    and status = '200 OK'
                group by path
                order by article_views desc
                limit 3;'''
    c.execute(query)
    results = c.fetchall()
    db.close()

    # Use Python string format!
    output = '\n   {:^42}\n\n'.format('Top Articles') # \n equals to an enter press
    output += '{:>23} | {:^19}\n'.format('Article Title', 'Reviewed Number')
    output += '{:-^45}\n'.format('') # - is the fill standard format specifier, filled all blank spaces with '-'

    for result in results:
        shortened_result_0 = result[0].replace('/article/', '')
        perfect_result_0 = shortened_result_0.replace('-', ' ')
        output += '{:>23} |{:^20}\n'.format(perfect_result_0, str(result[1])+' views')
    
    return output


def top_authors():
    """Return the name and their articles' total reviewed number of the top 4 authors"""
    db = psycopg2.connect(database = DBNAME)
    c = db.cursor()
    query = '''create view production as
            select authors.name, articles.title, textcat('/article/', articles.slug) as article_path
            from articles, authors
            where articles.author = authors.id;

            select production.name, count(*) as author_views
            from production, log
            where production.article_path = log.path
                and log.status = '200 OK'
            group by production.name
            order by author_views desc;
            '''
            # The log.status = '200 OK' is not necessary here, as 'article_path' already represents only the valid paths with 200 OK status
            # Those invalide paths which have status 404 NOT FOUND all have typos in their path, which are not equal to the textcat('/article/', articles.slug)
    c.execute(query)
    results = c.fetchall()
    db.close()

    # Use Python string format!
    output = '\n     {:^50}\n\n'.format('Top Authors') # \n equals to an enter press
    output += '{:>23} |{:^9}| {:^19}\n'.format('Authors Name', 'Ranking', 'Reviewed Number')
    output += '{:-^55}\n'.format('') # - is the fill standard format specifier, filled all blank spaces with '-'

    ranking = 1
    for result in results:
        output += '{:>23} |{:^9}| {:^19}\n'.format(result[0], str(ranking), str(result[1])+' views')
        ranking += 1
    
    return output


def abnormal_error_day():
    """Return the date when more than 1% of requests lead to errors and the asscociated request error percentage"""
    db = psycopg2.connect(database = DBNAME)
    c = db.cursor()
    query = '''create view request_summary as
            select time::date as request_date, count (*) as request_frequency
            from log
            group by request_date
            order by request_date;

            create view error_summary as
            select time::date as error_date, count (*) as error_frequency
            from log
            where status = '404 NOT FOUND'
            group by error_date
            order by error_date;

            create view all_summary as
            select error_date as date, error_frequency, request_frequency, 100 * (cast (error_frequency as float)/cast (request_frequency as float)) as error_percentage
            from error_summary inner join request_summary
            on error_date = request_date;

            select date, error_percentage
            from all_summary
            where error_percentage > 1;
            '''
    c.execute(query)
    results = c.fetchall()
    db.close()

    # Use Python string format!
    output = '\n{:^35}\n\n'.format('Abnormal Error Day') # \n equals to an enter press
    output += '{:>13} |{:^20}\n'.format('Date', 'Error Percentage')
    output += '{:-^35}\n'.format('') # - is the fill standard format specifier, filled all blank spaces with '-'

    for result in results:
        output += '{:>13} | {:^19}\n'.format(str(result[0]), str(result[1])+'%')
    
    return output


def generate_report(outputs, file_name, report_name = "A TBD string here", author = "Another TBD string here"):
    """Saves report information passed as a list of strings in the given
    directory with the given filename. This report is a plain text file."""
    header = '{:>17} {}\n{:>17} {}\n{:>17} {}\n\n'.format('Report Name:', report_name, 'Author:', author, 'Time Generated:', str(time.ctime()))
    
    content = '{:-^78}\n'.format('  Report Contents  ')
    for output in outputs:
        content += output + '\n'
    
    footer = '{:_^78}\n{:^78}'.format('', 'Format by J.C.')

    full_report = header + content + footer # The whole report contents are just strings!

    current_directory = os.getcwd()
    file_path = current_directory + '/' + file_name
    create_file = open(file_path, "w")
    create_file.write(full_report)
    create_file.close()
    print("File Created! at: " + file_path)


if __name__ == '__main__':
    top_3_articles = top_3_articles()
    top_authors = top_authors()
    abnormal_error_day = abnormal_error_day()

    report_name = "User Request Log Summary"
    author = "The Greatest Fullstack Dev JC"
    outputs = [top_3_articles, top_authors, abnormal_error_day]
    file_name = 'Final Output.txt'

    generate_report(outputs, file_name, report_name, author)