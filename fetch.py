from leetscrape.GetQuestionInfo import GetQuestionInfo

# Example: Fetching "3-sum"
try:
    q = GetQuestionInfo("3sum")
    data = q.scrape()
    print(data.body) # Description
    # You would then parse this and append to database.json
except:
    print("Could not fetch.")