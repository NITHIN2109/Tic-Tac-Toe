from flask import Flask, render_template, request, jsonify
from player import Player, HumanPlayer
from state import State

app = Flask(__name__)

# Load policies for both computer players
p1computer = Player("computer1", exp_rate=0)
p1computer.loadPolicy("policy_computer1")

p2computer = Player("computer2", exp_rate=0)
p2computer.loadPolicy("policy_computer2")

# Initialize state with default players
p1 = HumanPlayer("human")
p2 = p2computer
st = State(p1, p2)

# Variable to store user_choice
user_choice = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/choose_first_player", methods=["POST"])
def choose_first_player():
    global user_choice
    data = request.get_json()
    user_choice = data["choice"]

    # Set the player based on the user's choice
    global p1, p2, st
    if user_choice == "user":
        p1 = HumanPlayer("human")
        p2 = p2computer
    else:
        p1 = p1computer
        p2 = HumanPlayer("human")

    st = State(p1, p2)  # Reset st with new players

    # If computer is playing first, get its initial move
    if user_choice == "computer":
        computer_move = st.p1.chooseAction(
            st.availablePositions(), st.board, st.playerSymbol
        )
        st.updateState(computer_move)
        return jsonify(
            {
                "status": "success",
                "computer_move": computer_move,
                "board": st.board.tolist(),
            }
        )

    # Reset the game state
    st.reset()
    return jsonify({"status": "success"})


@app.route("/get_moves", methods=["POST"])
def get_moves():
    positions = st.availablePositions()
    return jsonify(positions)


@app.route("/make_move", methods=["POST"])
def make_move():
    global user_choice
    data = request.get_json()
    row = int(data["row"])
    col = int(data["col"])

    action = (row, col)

    positions = st.availablePositions()

    if action not in positions:
        return jsonify({"status": "error", "message": "Invalid move."})

    st.updateState(action)
    win = st.winner()

    if win is not None:
        result = {
            "status": "end",
            "winner": win,
            "board": st.board.tolist(),
        }
        st.reset()
        return jsonify(result)

    else:
        if user_choice == "user":
            action = st.p2.chooseAction(
                st.availablePositions(), st.board, st.playerSymbol
            )
        else:
            action = st.p1.chooseAction(
                st.availablePositions(), st.board, st.playerSymbol
            )

        st.updateState(action)
        win = st.winner()

        if win is not None:
            result = {
                "status": "end",
                "winner": win,
                "board": st.board.tolist(),
            }
            st.reset()
            return jsonify(result)

    return jsonify({"status": "continue", "board": st.board.tolist()})


if __name__ == "__main__":
    app.run(debug=True)
