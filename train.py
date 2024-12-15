from player import Player
from state import State

if __name__ == "__main__":
    p1 = Player("computer1")
    p2 = Player("computer2")

    st = State(p1, p2)
    print("training...")
    st.play(50000)
    p1.savePolicy()
    p2.savePolicy()
    print("training done")
