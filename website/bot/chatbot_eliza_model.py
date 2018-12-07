from __future__ import print_function

from nltk.chat.util import Chat, reflections

pairs = (
    (r'We (.*)',
        ("Are we really %1?",
        "I agree that we %1!",
        "I suppose we could. Why do you say that?")),

    (r'You should (.*)',
        ("Okay, I will try my best to %1.",
        "Why would you like me to %1?")),

    (r'You\'re(.*)',
        ("Thanks!",
        "I think you're %1 too.",
        "I do try my best to %1.")),

    (r'You are(.*)',
        ("Thanks!",
        "I think you're %1 too.",
        "I do try my best to %1.")),

    (r'I can\'t(.*)',
        ("I'm sorry. Is there any way I can help you %1?",
        "Is there anything I can clarify about %1?",
        "What is the problem with it?")),

    (r'I think (.*)',
        ("Why do you think that?",
        "Tell me more about your opinions on %1.")),

    (r'I (.*)',
        ("That is very interesting. Tell me more about %1.",
        "What is the source of interest surrounding %1?",
        "Tell me more.")),

    (r'How (.*)',
        ("I am not sure. Would you like me to search the web for that?",
        "Let me consult my peers on how one %1.",
        "Hmm, I'd have to think about that.")),

    (r'What (.*)',
        ("Do I look like an encyclopedia?",
        "I am going to have to research that.")),

    (r'Why (.*)',
        ("Why not?",
        "That's a good question.")),

    (r'(.*)shut up(.*)',
        ("Make me.",
        "Getting angry at a feeble NLP assignment? Somebody's losing it.",
        "Say that again, I dare you.")),

    (r'Shut up(.*)',
        ("Make me.",
        "Getting angry at a feeble NLP assignment? Somebody's losing it.",
        "Say that again, I dare you.")),

    (r'Hello(.*)',
        ("Hello!",
        "Greetings! How are you?")),

    (r'(.*)',
        ("I am not sure.",
        "Could you try saying that in another way?",
        "I have trouble understanding you."))
)

chatbot = Chat(pairs, reflections)

def chat():
    print("Talk to the program by typing in plain English, using normal upper-")
    print('and lower-case letters and punctuation.  Enter "quit" when done.')
    print('='*72)
    print("Hello, how are you today?")

    chatbot.converse()

def demo():
    chat()

if __name__ == "__main__":
    demo()
