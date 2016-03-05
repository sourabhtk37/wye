from datetime import datetime, timedelta

import base
from wye.base.constants import WorkshopStatus
from wye.regions.models import RegionalLead
from tests import factories as f

outbox_len = 0
password = '123123'


def test_workshop_list(base_url, browser, outbox):
    """
    Following testcases will be checked:
    - Check workshop listing for user with usertype poc
    - Check workshop listing for user with usertype tutor
    - Check workshop listing for user with usertype lead
    - Check workshop listing for user with no usertype
    """

    # Create usertypes
    poc_type = f.create_usertype(slug='poc', display_name='poc')
    tutor_type = f.create_usertype(slug='tutor', display_name='tutor')
    regional_lead_type = f.create_usertype(slug='lead', display_name='regional lead')

    # Testcase with usertyep poc
    user = base.create_user(password)
    url = base_url + '/workshop/'
    base.login_and_confirm(browser, url, outbox, user, password)
    user.profile.usertype.add(poc_type)
    user.save()

    # Create org
    org = f.create_organisation()
    org.user.add(user)
    user.profile.interested_locations.add(org.location)
    org.save()

    # Create workshop
    workshop = f.create_workshop(requester=org)
    workshop.expected_date = datetime.now() + timedelta(days=20)
    workshop.status = WorkshopStatus.REQUESTED
    workshop.location = org.location
    workshop.save()

    url = base_url + '/workshop/'
    base.login(browser, url, user, password)
    data_check = browser.find_by_text(org.name)
    assert data_check

    # Testcase for usertype tutor
    browser.visit(base_url + "/accounts/logout")
    user = base.create_user(password)
    url = base_url + '/workshop/'
    base.login_and_confirm(browser, url, outbox, user, password)
    user.profile.usertype.add(tutor_type)
    user.save()

    url = base_url + '/workshop/'
    base.login(browser, url, user, password)
    # User not associate with workshop
    data_check = browser.find_by_text(org.name)
    assert [] == data_check

    # User associated with workshop
    workshop.presenter.add(user)
    browser.visit(url)
    data_check = browser.find_by_text(org.name)
    assert data_check

    # Testcase for lead
    browser.visit(base_url + "/accounts/logout")
    user = base.create_user(password)
    url = base_url + '/workshop/'
    base.login_and_confirm(browser, url, outbox, user, password)

    user.profile.usertype.add(regional_lead_type)
    user.save()
    lead = RegionalLead.objects.create(location=org.location)
    lead.leads.add(user)

    url = base_url + '/workshop/'
    base.login(browser, url, user, password)
    data_check = browser.find_by_text(org.name)
    assert data_check

    # Testcase for user with no usertype
    browser.visit(base_url + "/accounts/logout")
    user = base.create_user(password)
    url = base_url + '/workshop/'
    base.login_and_confirm(browser, url, outbox, user, password)

    url = base_url + '/workshop/'
    base.login(browser, url, user, password)
    data_check = browser.find_by_text(org.name)
    assert [] == data_check