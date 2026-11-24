from pathlib import Path

import os
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]

with sync_playwright() as p, TemporaryDirectory() as temp:
    browser = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH"))
    page = browser.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto((ROOT / "index.html").as_uri())
    answer = page.locator("#result").inner_text().splitlines()[0].split(" · ")[1]
    assert abs(float(answer.replace(",", "")) - 28) < 0.00001
    with page.expect_download() as exported:
        page.locator("#save").click()
    dest = Path(temp) / "result.txt"
    exported.value.save_as(dest)
    assert dest.read_text(encoding="utf-8") == page.locator("#result").inner_text()
    page.locator("#f0").fill("")
    assert page.locator("#save").is_disabled()
    assert not errors, errors
    browser.close()
