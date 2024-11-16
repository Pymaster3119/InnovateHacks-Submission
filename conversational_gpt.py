import gpt_interactor
import os
from googlesearch import search
import navigation_gpt
import time
import json

with open("static/conversation.txt", "w") as txt:
    txt.write("")

searchavailable = True

with open("conversational_gpt_input_text.txt", "r") as txt:
    systemtext = txt.read()

#Interactions with UI
def send_message(message):
    print("--------------------------------------------------------------")
    print(f"Sent to user: {message}")

    with open("static/conversation.txt", "a") as txt:
        txt.write(json.dumps({
            "role": "assistant",
            "content": message
        }).replace("\\n", "<br>") +"\n")
    output = ""
    with open("static/action.txt", "r") as txt:
        actioncontents = txt.read()
    while True:
        with open("static/action.txt", "r") as txt:
            contents = txt.read()
            if contents != actioncontents:
                output = contents
                break
        time.sleep(0.5)
    with open("static/conversation.txt","a") as txt:
        txt.write("{" + f"\"role\":\"user\",\"content\":\"{output}\"" + "}\n")

    
    print(f"Recieved from user: {contents}")
    print("--------------------------------------------------------------")
    return output

#Function definitions
def search_curator(prompt):
    with open("static/conversation.txt","a") as txt:
        txt.write('{"role":"interjection","content":"Searching..."}\n')
    with open("searchgpt", "r") as txt:
        system_text = txt.read() + prompt
    results = search(prompt)
    formattedresults = ""
    searchresults = 0
    for j in results:
        if searchresults < 10:
            formattedresults += j + "\n"
            searchresults += 1
        else:
            break
    gpt_response = gpt_interactor.run_query(system_text=system_text, user_prompt=formattedresults)
    print("--------------------------------------------------------------")
    print(f"Search query: {prompt}")
    print(f"GPT Response: {gpt_response}")
    print("--------------------------------------------------------------")
    navigation_gpt.get_website(gpt_response)
    navigation_gpt.time.sleep(5)
    navigation_gpt.take_full_page_png(f"result.png")
    return "Saved Image"

def invoke_navigator(prompt):
    with open("static/conversation.txt","a") as txt:
        txt.write('{"role":"interjection","content":"Navigating webpage..."}\n')
    print("--------------------------------------------------------------")
    print("Started Navigation")
    navigation_gpt.navigate_around_current_website(prompt)
    print("Ended Navigation")
    print("--------------------------------------------------------------")
    return "Saved Image"

#Define functions for Mr. GPT
search_curator_function = gpt_interactor.function(
    name="search_curator",
    description="This function searches for the prompt you provide and returns the most relavent link",
    params = [{"name":"prompt", "type":"string", "description":"The optimized search prompt you want to use"}],
    callback=search_curator,
    outputname="Status"
)
invoke_navigator_function = gpt_interactor.function(
    name="invoke_navigator",
    description="This function sends a given prompt to the web navigator, which will then return a screenshot of the website",
    params = [{"name":"prompt", "type":"string", "description":"The simple, managable prompt given to the web navigator"}],
    callback = invoke_navigator,
    outputname="Status"
)


gptmessage = "How can I help you today?"
messages = [{"role": "system", "content": systemtext}, {"role":"assistant", "content": gptmessage}]

while True:
    userinput = send_message(gptmessage)
    gptmessage = gpt_interactor.run_query(gpt_model="gpt-4o",system_text=systemtext, user_prompt=userinput, messages = messages, functions = [search_curator_function, invoke_navigator_function])
