
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent


#just creating a agent withot tools for demo purpose
#agent without the tool is just a chatbot


# create model
llm = init_chat_model(
    model = "google/gemma-3-4b",
    model_provider = "openai",
    base_url = "http://127.0.0.1:1234/v1",
    api_key = "non-needed"
)

# conversation context
conversation = []
# create agent
agent = create_agent(model=llm, 
            tools=[],
            system_prompt="You are a helpful assistant. Answer in short."
        )

while True:
    # take user input
    user_input = input("You: ")
    if user_input == "exit":
        break
    # append user message in coversation
    conversation.append({"role": "user", "content": user_input})
    # invoke the agent
    result = agent.invoke({"messages": conversation})

    # print the result's last message

    # messages is a list of messages in the conversation
    #[-1] gives AImessage
    #[-2] gives user message
    # .content gives the content of the message

    ai_msg = result["messages"][-1]
    print("AI: ", ai_msg.content)
    # let's use conversation history returned by agent
    conversation = result["messages"]