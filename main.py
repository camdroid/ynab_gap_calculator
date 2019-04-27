import requests
import pdb
from secrets import API_KEY, budget_id, credit_card_group_category

BASE_URL = 'https://api.youneedabudget.com/v1/'


def ynab_get(path, params=None):
    url = BASE_URL + path
    headers = {
        'Authorization': 'Bearer {}'.format(API_KEY)
    }
    res = requests.get(url, params=params, headers=headers)
    data = res.json()['data']
    return data


def get_budget_id_by_name(name):
    path = 'budgets'
    res = ynab_get(path)
    budgets = res['budgets']
    b = [budget for budget in budgets
            if budget['name']==name]
    return b[0]['id']


def get_main_budget_id():
    return get_budget_id_by_name('My Budget')


def get_real_estate_budget_id():
    return get_budget_id_by_name('Real Estate')


# budget_id = get_main_budget_id()
# print(budget_id)

def get_list_of_categories(budget_id):
    path = f'budgets/{budget_id}/categories'
    res = ynab_get(path)
    category_groups = res['category_groups']
    categories = {}
    for category_group in category_groups:
        for category in category_group['categories']:
            categories[category['id']] = category['name']
    return categories

def strip_category_dict(budget_dict):
    return {k: budget_dict[k] for k in ('activity', 'balance', 'budgeted', 'id')}


def get_budget_for_month(budget_id, month):
    path = f'budgets/{budget_id}/months/2019-{month}-01'
    res = ynab_get(path)
    categories = res['month']['categories']
    d_cat = {cat['name']: strip_category_dict(cat) 
             for cat in categories
             if not cat['deleted'] and not cat['hidden']
               and not cat['category_group_id'] == credit_card_group_category
               and not cat['name'] == 'To be Budgeted'}
    return d_cat

categories = get_list_of_categories(budget_id)
may = get_budget_for_month(budget_id, 5)
april = get_budget_for_month(budget_id, 4)

def cat_gap(category_name, month_0, month_1):
    # Activity will usually be negative, so add if you want to get the difference
    return month_1[category_name]['balance'] + month_0[category_name]['activity']

gap = {cat_name: cat_gap(cat_name, may, april)
       for cat_name in may.keys()}

gap = {k: v for (k, v) in gap.items() if v != 0}
print(sum([v for v in gap.values()])/1000)

