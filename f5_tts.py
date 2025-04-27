import replicate

replicate_client = replicate.Client(api_token="r8_B5Riax1c95EAkwcZFzXiLjds4h1x9Tm43x3OF")

ref_audio = open("test1.wav", "rb")
input = {
    "gen_text": "I don’t like cats and they don’t like me. I used to be allergic to them and I would get stuffed up and have hives.",
    "ref_text": "",
    "ref_audio": ref_audio
}

output = replicate_client.run(
    "x-lance/f5-tts:87faf6dd7a692dd82043f662e76369cab126a2cf1937e25a9d41e0b834fd230e",
    input=input
)

with open("output.wav", "wb") as file:
    file.write(output.read())
