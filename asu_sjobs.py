#!/usr/bin/env python

from __future__ import unicode_literals
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import config
import os
os.environ["LANG"] = "en_US.UTF-8"


def load_applied_jobs():
    with open(config.applied_jobs_file, 'r') as f:
        return set(f.read().splitlines())


def save_applied_jobs(applied_jobs):
    applied_jobs = list(dict.fromkeys(applied_jobs))
    with open(config.applied_jobs_file, 'w') as f:
        f.write('\n'.join(applied_jobs))


def already_applied(driver):
    try:
        driver.find_element_by_css_selector("#appLbl")
    except NoSuchElementException:
        return False
    return True


def apply_to_job(job_link, driver):
    try:
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(job_link)
        if already_applied(driver):
            return job_link
        driver.find_element_by_css_selector(
            "#applyFromDetailBtn > span.ladda-label").click()
        driver.find_element_by_css_selector("#startapply").click()
        driver.find_element_by_css_selector("#shownext").click()
        driver.find_element_by_css_selector("#radio-44674-Yes").click()
        driver.find_element_by_css_selector("#radio-61829-Yes").click()
        driver.find_element_by_css_selector(
            "#custom_44925_1291_fname_slt_0_44925-button_text").click()
        driver.find_element_by_css_selector("#ui-id-5").click()
        driver.find_element_by_css_selector("#shownext").click()
        driver.find_element_by_css_selector("#AddResumeLink").click()
        driver.switch_to.frame(driver.find_element_by_id("profileBuilder"))
        driver.find_element_by_css_selector("#btnSelectedSavedRC").click()
        driver.find_elements_by_xpath('//*[@id="FileList"]')[-1].click()
        driver.find_element_by_css_selector(
            "body > div.encompassingDiv.ImportProfile.ng-scope > div > div:nth-child(5) > div > div.Marginbottom20.clearfix > button").click()
        driver.switch_to.default_content()
        driver.find_element_by_css_selector("#AddCLLink").click()
        driver.switch_to.frame(driver.find_element_by_id("profileBuilder"))
        driver.find_element_by_css_selector("#btnSelectedSavedRC").click()
        driver.find_elements_by_xpath('//*[@id="FileList"]')[-1].click()
        driver.find_element_by_css_selector(
            "body > div.encompassingDiv.ImportProfile.ng-scope > div > div:nth-child(5) > div > div.Marginbottom20.clearfix > button").click()
        driver.switch_to.default_content()
       # driver.find_element_by_css_selector(
       #     "#profile_16_0_lnpronunciationkey_txt_0").send_keys(config.preferred_name)
        driver.find_element_by_css_selector("#shownext").click()
        driver.find_element_by_css_selector(
            "#attachmentWidget > div > div.fieldcontain > p > a").click()
        driver.switch_to.frame(driver.find_element_by_id("profileBuilder"))
        driver.find_element_by_css_selector("#btnSelectedSavedRC").click()
        for el in driver.find_elements_by_xpath('//*[@id="FileList"]'):
            if el.find_element_by_tag_name('label').text in config.file_list:
                el.click()
        time.sleep(0.5)
        driver.find_element_by_css_selector(
            "body > div.encompassingDiv.ImportProfile.ng-scope > div > div:nth-child(5) > div > div.Marginbottom20.clearfix > button").click()
        driver.switch_to.default_content()
        driver.find_element_by_css_selector("#shownext").click()
        WebDriverWait(driver, config.TIMEOUT).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "#custom_42326_1300_fname_txt_0"))
        )
        driver.find_element_by_css_selector("#shownext").click()
        WebDriverWait(driver, config.TIMEOUT).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "#radio-42285-Undisclosed"))
        )
        driver.find_element_by_css_selector("#shownext").click()
        WebDriverWait(driver, config.TIMEOUT).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "#checkbox-44744-Asian"))
        )
        driver.find_element_by_css_selector("#shownext").click()
        if not config.disable_save_submit:
            driver.implicitly_wait(2)
            driver.find_element_by_css_selector("#save").click()
            time.sleep(0.5)
            return job_link
        time.sleep(0.5)

    except Exception as e:
        return


if __name__ == '__main__':
    driver = webdriver.Chrome(executable_path="./chromedriver.exe")
    driver.capabilities.update()
    driver.maximize_window()
    driver.get("https://students.asu.edu/employment/search")
    # WebDriverWait(driver, config.TIMEOUT).until(
    #     EC.visibility_of_element_located(
    #         (By.CSS_SELECTOR, "#node-16685 > div > div.field.field-name-body.field-type-text-with-summary.field-label-hidden > div > div > div > div:nth-child(1) > a > button"))
    # )
    time.sleep(0.5)
    driver.find_element_by_css_selector(
        "#node-16685 > div > div.field.field-name-body.field-type-text-with-summary.field-label-hidden > div > div > div > div:nth-child(1) > a > button").click()
    time.sleep(0.5)
    WebDriverWait(driver, config.TIMEOUT).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#username"))
    )
    driver.find_element_by_id('username').send_keys(config.username)
    driver.find_element_by_id('password').send_keys(config.password)
    driver.find_element_by_name('submit').click()

    WebDriverWait(driver, config.TIMEOUT).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#initialSearchBox > div > h1"))
    )
    driver.implicitly_wait(4)
    results = int(driver.find_element_by_css_selector(
        "#initialSearchBox > div > h1").get_attribute("innerHTML").split()[3])

    WebDriverWait(driver, config.TIMEOUT).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#searchControls_BUTTON_2"))
    )
    driver.find_element_by_id('searchControls_BUTTON_2').click()

    time.sleep(1)
    for i in range(int(results/50)):
        driver.implicitly_wait(2)
        WebDriverWait(driver, config.TIMEOUT).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "#showMoreJobs"))
        )
        driver.find_element_by_css_selector("#showMoreJobs").click()

    job_links = []

    for i in range(results):
        job_links.append(driver.find_element_by_css_selector(
            f"#Job_{i}").get_attribute("href"))

    applied_jobs = load_applied_jobs()
    job_links = list(set(job_links) - set(applied_jobs))

    if config.max_jobs:
        job_links = job_links[:config.max_jobs]

    print("Total jobs to be applied: " + str(len(job_links)))

    applied_jobs = list(applied_jobs)

    for i, job_link in enumerate(job_links):
        try:
            if i % 10 == 0:
                save_applied_jobs(applied_jobs)
            appled_job = apply_to_job(job_link, driver)
            if appled_job:
                applied_jobs.append(appled_job)

        except Exception as e:
            continue

    save_applied_jobs(applied_jobs)

    print("Execution Complete")
    driver.refresh()
    driver.close()
    driver.quit()
