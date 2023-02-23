from django.shortcuts import render, redirect
from django.db import connection
import csv, os

def displayMain(request):
    allStudents = []
    allProfessors = []
    allCounties = []
    allCovids = []
    query1Results = []
    query2Results = []
    query3Results = []
    query4Results = []
    query5Results = []


    with connection.cursor() as cursor:
        # retrieve all student records from DB
        retrieveStudQuery = "SELECT * FROM Students;"
        cursor.execute(retrieveStudQuery)
        fetchedStudRecords = cursor.fetchall()

        # retrieve all professor records from DB
        retrieveProfQuery = "SELECT * FROM Professors;"
        cursor.execute(retrieveProfQuery)
        fetchedProfRecords = cursor.fetchall()

        # retrieve all county records from DB
        retrieveCountyQuery = "SELECT * FROM Counties;"
        cursor.execute(retrieveCountyQuery)
        fetchedCountyRecords = cursor.fetchall()

        # retrieve all covid records from DB
        retrieveCovidQuery = "SELECT * FROM COVID;"
        cursor.execute(retrieveCovidQuery)
        fetchedCovidRecords = cursor.fetchall()

        # Get Result of Query #1
        query1 = "SELECT countyName, AVG(score) "       \
                    "FROM Counties c, Students s "      \
                    "WHERE c.countyName = s.county "    \
                    "GROUP BY countyName "              \
                    "ORDER BY countyName;"
        cursor.execute(query1)
        fetchedQuery1Result = cursor.fetchall()

        # Get Result of Query #2
        query2 = "SELECT city, AVG(score) "             \
                    "FROM Counties c, Students s "      \
                    "WHERE c.countyName = s.county "    \
                    "GROUP BY city "                    \
                    "ORDER BY city;"
        cursor.execute(query2)
        fetchedQuery2Result = cursor.fetchall()

        # Get Result of Query #3
        query3 = "SELECT op.name AS profName, fs.name AS studName "                                                         \
                "FROM "                                                                                                     \
                "( "                                                                                                        \
	                "SELECT name, prof.county "                                                                             \
	                "FROM Professors prof, ( SELECT county, max(age) as oldage FROM Professors GROUP BY county ) oldest "   \
	                "WHERE prof.county = oldest.county AND prof.age >= oldest.oldage "                                      \
                ") op, "                                                                                                    \
                "( "                                                                                                        \
	            "SELECT name, stud.county "                                                                                 \
	            "FROM Students stud, ( SELECT county, max(score) as maxscore FROM Students GROUP BY county ) firstplace "   \
	            "WHERE stud.county = firstplace.county AND stud.score >= firstplace.maxscore "                              \
                ") fs "                                                                                                     \
                "WHERE op.county = fs.county "                                                                              \
                "ORDER BY op.county;"
        cursor.execute(query3)
        fetchedQuery3Result = cursor.fetchall()

        # Get Result of Query #4
        query4 = "SELECT op.name AS profName, fs.name AS studName "                                                                                                                     \
                "FROM "                                                                                                                                                                 \
                "( "                                                                                                                                                                    \
                    "SELECT prof.name, oldest.city "                                                                                                                                    \
                    "FROM Professors prof, Counties cnt, ( SELECT city, max(age) as oldage FROM Professors p, Counties c WHERE p.county = c.countyName GROUP BY c.city ) oldest "       \
                    "WHERE prof.county = cnt.countyName AND cnt.city = oldest.city AND prof.age >= oldest.oldage "                                                                      \
                ") op, "                                                                                                                                                                \
                "( "                                                                                                                                                                    \
                    "SELECT stud.name, firstplace.city "                                                                                                                                \
                    "FROM Students stud, Counties cnt, ( SELECT city, max(score) as maxscore FROM Students s, Counties c WHERE s.county = c.countyName GROUP BY c.city ) firstplace "   \
                    "WHERE stud.county = cnt.countyName AND cnt.city = firstplace.city AND stud.score >= firstplace.maxscore "                                                          \
                ") fs "                                                                                                                                                                 \
                "WHERE op.city = fs.city "                                                                                                                                              \
                "ORDER BY op.city;"
        cursor.execute(query4)
        fetchedQuery4Result = cursor.fetchall()

        # Get Result of Query #5
        query5 = "SELECT stud.name AS studName, dangercities.city as cityName "                 \
                "FROM Students stud, Counties c, "                                              \
                "( "                                                                            \
	                "SELECT cities.city, (infested.cnt / cities.totalpopulation) AS ratio "     \
	                "FROM "                                                                     \
	                "( "                                                                        \
		                "SELECT city, COUNT(patientID) AS cnt "                                 \
		                "FROM COVID "                                                           \
		                "GROUP BY COVID.city "                                                  \
	                ") infested, "                                                              \
	                "( "                                                                        \
                        "SELECT city, SUM(population) as totalpopulation "                      \
                        "FROM Counties "                                                        \
                        "GROUP BY city "                                                        \
	                ") cities "                                                                 \
	                "WHERE infested.city = cities.city "                                        \
	                "ORDER BY ratio DESC "                                                      \
	                "LIMIT 3 "                                                                  \
                ") dangercities "                                                               \
                "WHERE stud.county = c.countyName AND c.city = dangercities.city;"
        cursor.execute(query5)
        fetchedQuery5Result = cursor.fetchall()

        # close connection
        connection.commit()
        connection.close()

        # append 'ALL' records
        for studRecord in fetchedStudRecords:
            eachRow = {'studentID': studRecord[0], 'name': studRecord[1], 'score': studRecord[2], 'county': studRecord[3]}
            allStudents.append(eachRow)

        for profRecord in fetchedProfRecords:
            eachRow = {'facultyID': profRecord[0], 'name': profRecord[1], 'age': profRecord[2], 'county': profRecord[3]}
            allProfessors.append(eachRow)

        for countyRecord in fetchedCountyRecords:
            eachRow = {'countyName': countyRecord[0], 'population': countyRecord[1], 'city': countyRecord[2]}
            allCounties.append(eachRow)

        for covidRecord in fetchedCovidRecords:
            eachRow = {'patientID': covidRecord[0], 'city': covidRecord[1]}
            allCovids.append(eachRow)

        # append Results of Queries
        for record in fetchedQuery1Result:
            eachRow = {'countyName': record[0], 'averageScore': round(record[1], 4)}
            query1Results.append(eachRow)

        for record in fetchedQuery2Result:
            eachRow = {'cityName': record[0], 'averageScore': round(record[1], 4)}
            query2Results.append(eachRow)

        for record in fetchedQuery3Result:
            eachRow = {'professorName': record[0], 'studentName': record[1]}
            query3Results.append(eachRow)

        for record in fetchedQuery4Result:
            eachRow = {'professorName': record[0], 'studentName': record[1]}
            query4Results.append(eachRow)

        for record in fetchedQuery5Result:
            eachRow = {'studentName': record[0], 'cityName': record[1]}
            query5Results.append(eachRow)

    return render(request, 'peopleInfo/main.html', {"students": allStudents, "professors": allProfessors, "counties": allCounties, "covids": allCovids,
                                                    "query1Results": query1Results, "query2Results": query2Results, "query3Results": query3Results,
                                                    "query4Results": query4Results, "query5Results": query5Results })


def addStudents(request):
    # get directory of csv file
    workpath = os.path.dirname(os.path.abspath(__file__)) # returns the path of this .py file is in
    csvdir = os.path.join(workpath, "templates\\peopleInfo\\students.csv")

    # open csv file
    file = open(csvdir, 'r')
    studRecords = csv.reader(file)  # list of student record

    with connection.cursor() as cursor:
        # insert student records from csv
        queryTemplate = "REPLACE INTO Students(studentID, name, score, county) VALUES ('{0}', '{1}', {2}, '{3}');"
        for record in studRecords:
            query = queryTemplate.format(record[0], record[1], float(record[2]), record[3])
            cursor.execute(query)

        connection.commit()
        connection.close()

    file.close()

    return redirect('/')


def addProfessors(request):
    # get directory of csv file
    workpath = os.path.dirname(os.path.abspath(__file__)) # returns the path of this .py file is in
    csvdir = os.path.join(workpath, "templates\\peopleInfo\\professors.csv")

    # open csv file
    file = open(csvdir, 'r')
    profRecords = csv.reader(file)

    with connection.cursor() as cursor:
        # insert professor records from csv
        queryTemplate = "REPLACE INTO Professors(facultyID, name, age, county) VALUES ('{0}', '{1}', {2}, '{3}');"
        for record in profRecords:
            query = queryTemplate.format(record[0], record[1], int(record[2]), record[3])
            cursor.execute(query)

        connection.commit()
        connection.close()

    file.close()

    return redirect('/')

def addCounties(request):
    # get directory of csv file
    workpath = os.path.dirname(os.path.abspath(__file__)) # returns the path of this .py file is in
    csvdir = os.path.join(workpath, "templates\\peopleInfo\\counties.csv")

    # open csv file
    file = open(csvdir, 'r')
    countyRecords = csv.reader(file)

    with connection.cursor() as cursor:
        # insert county records from csv
        queryTemplate = "REPLACE INTO Counties(countyName, population, city) VALUES ('{0}', {1}, '{2}');"
        for record in countyRecords:
            query = queryTemplate.format(record[0], int(record[1]), record[2])
            cursor.execute(query)

        connection.commit()
        connection.close()

    file.close()

    return redirect('/')

def addCovids(request):
    # get directory of csv file
    workpath = os.path.dirname(os.path.abspath(__file__)) # returns the path of this .py file is in
    csvdir = os.path.join(workpath, "templates\\peopleInfo\\covid.csv")

    # open csv file
    file = open(csvdir, 'r')
    covidRecords = csv.reader(file)

    with connection.cursor() as cursor:
        # insert COVID records from csv
        queryTemplate = "REPLACE INTO COVID(patientID, city) VALUES ('{0}', '{1}');"
        for record in covidRecords:
            query = queryTemplate.format(record[0], record[1])
            cursor.execute(query)

        connection.commit()
        connection.close()

    file.close()

    return redirect('/')