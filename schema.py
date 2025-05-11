import argparse
import requests
import sys

def get_bot_schema(jwt, uuid):
    url = f"http://147.45.105.16:8400/api/bots/{uuid}?jwtToken={jwt}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def generate_dot(schema):
    dot = [
        'digraph BotGraph {',
        '  node [shape=box];',
        '  rankdir=UD;',
        '  _start [shape=point, width=0, style=invis];'
    ]

    transitions = []
    node_details = {}

    for block in schema["blocks"]:
        node_id = str(block["state"])
        
        style = {
            "question": 'fillcolor="#71bbc1", style=filled',
            "selection": 'fillcolor="#878dbf", style=filled',
            "message": 'fillcolor="#b9e3c2", style=filled'
        }.get(block["type"], "")
        
        node_details[node_id] = f'  {node_id} [label="{block.get("text", "")}", {style}];'

        if block["type"] == "selection":
            for option in block.get("options", []):
                transitions.append((
                    node_id,
                    str(option["next"]),
                    option["text"].replace('\\', r'\\').replace('"', r'\"')
                ))
        elif "nextState" in block and block["nextState"] != 0:
            transitions.append((
                node_id,
                str(block["nextState"]),
                None
            ))

    dot.append(f'  _start -> {str(schema["entries"][0]["state"])};')
    dot.extend(node_details.values())
    
    for src, dst, label in transitions:
        if src in node_details and dst in node_details:
            if label:
                dot.append(f'  {src} -> {dst} [label="{label}"];')
            else:
                dot.append(f'  {src} -> {dst};')

    dot.append('}')
    return '\n'.join(dot)

def main():
    parser = argparse.ArgumentParser(description="Generate Graphviz DOT from MockAPI")
    parser.add_argument("jwt", help="JWT токен")
    parser.add_argument("uuid", help="Bot UUID")
    args = parser.parse_args()

    try:
        print(generate_dot(get_bot_schema(args.jwt, args.uuid)))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()