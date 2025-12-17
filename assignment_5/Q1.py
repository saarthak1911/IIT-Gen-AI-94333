from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tabulate import tabulate
from textwrap import fill
import time


table_data1 = []
table_data2= []

driver = webdriver.Chrome()
driver.get("https://www.sunbeaminfo.in/about-us")

wait = WebDriverWait(driver, 10)

driver.find_element(By.LINK_TEXT, "INTERNSHIP").click()

wait.until(
    EC.element_to_be_clickable((By.XPATH, "//a[@aria-controls='collapseSix']"))
).click()

accordion_content = wait.until(
    EC.visibility_of_element_located((By.ID, "collapseSix"))
)

rows = accordion_content.find_elements(By.XPATH, ".//tbody/tr")
for row in rows:
    cols = row.find_elements(By.TAG_NAME, "td")
    table_data1.append([col.text for col in cols])

headers = ["Technology", "Aim", "Prerequisite", "Learning", "Location"]

def wrap_row(row, width=35):
    return [fill(cell, width=width) for cell in row]

wrapped_data = [wrap_row(row) for row in table_data1]

print("Available Internship Program")
print(tabulate(wrapped_data, headers=headers, tablefmt="fancy_grid"))

# --------------------------------------------------------------------------------------------------------------------------

accordion_content2 = wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME,"table-responsive"))
    )

rows2 = accordion_content2.find_elements(By.XPATH, ".//tbody/tr")
for row in rows2:
        cols = row.find_elements(By.TAG_NAME, "td")
        table_data2.append([col.text for col in cols])

headers = ["Sr.No", "Batch","Batch Duration","Start Date","End Date","Time","Fees(Rs.)","Download Brochure"]

def wrap_row(row, width=35):
        return [fill(cell, width=width) for cell in row]

wrapped_data2 = [wrap_row(row) for row in table_data2]
print("\nInternship Batches Schedule :")
print(tabulate(wrapped_data2, headers=headers, tablefmt="fancy_grid"))


time.sleep(10)
driver.quit()