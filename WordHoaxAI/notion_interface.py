import os

print()

import requests, json

token = os.getenv("NOTION_API_KEY")

databaseId = '75bdbda3c7234d0f83034e80177229f5'

# https://honored-mandolin-bf6.notion.site/75bdbda3c7234d0f83034e80177229f5?v=d0c196c305814d32b06b04cc7732f936

headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2021-05-13"
}


def get_v_for_all_with_key_in_dict_tree(tree, key):
    # print("-new call-")
    for k, v in tree.items():
        # print(k)
        if type(v) == dict:
            # print("is dict")
            if key in v.keys():
                # print(f"yielding{v[key]} from: {tree}")
                yield v[key]
            else:
                for a in get_v_for_all_with_key_in_dict_tree(v, key):
                    yield a
        if type(v) == list:
            # print("is list")
            for item in v:
                if type(item) == dict:
                    for a in get_v_for_all_with_key_in_dict_tree(item, key):
                        yield a
        if type(k) == str:
            if k == key:
                yield v
        else:
            pass


def update_database_from_notion(database_id, headers):
    all_results = []

    readUrl = f"https://api.notion.com/v1/databases/{database_id}/query"

    res = requests.request("POST", readUrl, headers=headers)
    data = res.json()
    print(res.status_code)
    print(res.text)
    decoded = json.loads(res.text)
    all_results.append(decoded['results'])

    while data["has_more"]:
        all_results.append(decoded['results'])
        has_more = data["has_more"]
        next_cursor = data["next_cursor"]
        print(has_more, next_cursor)

        res = requests.request("POST", readUrl, headers=headers, json={"start_cursor": next_cursor})
        data = res.json()
        decoded = json.loads(res.text)

    records = []
    for results in all_results:
        for result in results:
            item = result['properties']['Name']['title'][0]['text']["content"].replace("\n", "")
            speech = [a for a in get_v_for_all_with_key_in_dict_tree(result['properties']['property'], "name")]
            botz = [a for a in get_v_for_all_with_key_in_dict_tree(result['properties']['Botz'], "name")]
            records.append((item, speech, botz))

    for record in records:
        print(record)

    with open('./dictionary_for_personalities.json', 'w', encoding='utf8') as f:
        json.dump(records, f, ensure_ascii=False)


# Create a Page
def create_page(databaseId, headers):
    createUrl = 'https://api.notion.com/v1/pages'

    newPageData = {
        "parent": {"database_id": databaseId},
        "properties": {
            "Description": {
                "title": [
                    {
                        "text": {
                            "content": "Review"
                        }
                    }
                ]
            },
            "Value": {
                "rich_text": [
                    {
                        "text": {
                            "content": "Amazing"
                        }
                    }
                ]
            },
            "Status": {
                "rich_text": [
                    {
                        "text": {
                            "content": "Active"
                        }
                    }
                ]
            }
        }
    }

    data = json.dumps(newPageData)
    # print(str(uploadData))

    res = requests.request("POST", createUrl, headers=headers, data=data)

    print(res.status_code)
    print(res.text)


# Update a Page
def update_page(pageId, headers):
    updateUrl = f"https://api.notion.com/v1/pages/{pageId}"

    updateData = {
        "properties": {
            "Value": {
                "rich_text": [
                    {
                        "text": {
                            "content": "Pretty Good"
                        }
                    }
                ]
            }
        }
    }

    data = json.dumps(updateData)

    response = requests.request("PATCH", updateUrl, headers=headers, data=data)

    print(response.status_code)
    print(response.text)


if __name__ == "__main__":
    update_database_from_notion(databaseId, headers)
