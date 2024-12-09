# Job parsing for French-language positions in the cybersecurity field on job portals

This project was proposed by the cybersecurity-related internship company I work for. The goal is to develop a parser to extract freelance job information related to cybersecurity from job portals like [Indeed](https://fr.indeed.com/), [Free-work](https://www.free-work.com/fr/tech-it), and [Insitoo](https://insitoo.com/). The extracted information will be automatically updated on the company's website.

This project consists of five sub-tasks: Web scraping, detection of duplicate job postings, detection of false positives, automatic categorization of job postings, and updating. Additionally, there will be an overarching script named [run_scripts.py](run_scripts.py) that can sequentially execute these tasks to achieve the goal of automated site parsing.

# Installation

Please see [requirements.txt](requirements.txt) for installation.

Before running these codes, you need to set the following in [settings.py](settings.py):


```python
API_KEY_SCRAPEOPS = ""
API_KEY_OPENAI = ""
```

The above two API keys need to be obtained from [ScrapeOps](https://scrapeops.io/?fpr=lucas37&gad_source=1&gclid=Cj0KCQiAx9q6BhCDARIsACwUxu5p1vYgJippslx3S7qqfowqE5V1nYVpzffv0Zaq5hB_sbjVz97bqWQaAo2HEALw_wcB) and [OpenAI](https://platform.openai.com/docs/overview).

You also need to configure the [config.json](config.json) file with the job search websites you want to scrape. Currently, only French-language versions of **Indeed**, **free-work**, and **Insitoo** are supported. For example:


```python
{"startUrl":[

"https://insitoo.com/mission-freelance/?region=Toutes+les+r%C3%A9gions&search=cyber+s%C3%A9curit%C3%A9",
"https://www.free-work.com/fr/tech-it/jobs?contracts=contractor&query=cissp&freshness=from_1_to_7_days",
"https://fr.indeed.com/emplois?q=cyber+securit%C3%A9&l=Paris+%2875%29&sc=0kf%3Ajt%28subcontract%29%3B"

]
}
```

# Approach

The most straightforward method is to run [run_scripts.py](run_scripts.py), which will scrape the website pages you mentioned, perform data cleaning, and then update the information in the [data](data) folder.
