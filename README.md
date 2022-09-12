# GamesList
A way to organize games you are playing, have played, want to play, etc..

## Usage
### View your listed games

![Screenshot from 2022-09-12 19-10-02](https://user-images.githubusercontent.com/101006560/189726260-9e88ab51-2135-4bbd-860f-6692181888db.png)

Each game has a title, a status, a console and you can choose to give a score as well. Games can be sorted by those features

![Screenshot from 2022-09-12 19-11-16](https://user-images.githubusercontent.com/101006560/189727137-7905ac2c-183f-4bb0-9e03-cfc2f406401c.png)

If you're looking for a specific game in your list, you can search for it

![Screenshot from 2022-09-12 19-16-23](https://user-images.githubusercontent.com/101006560/189727517-54311ce6-561f-4d6e-adf6-b9f58b40fe6e.png)

### Add new games
New games can easily be added to the list, and changes to the list are immediately saved

![Screenshot from 2022-09-12 19-12-07](https://user-images.githubusercontent.com/101006560/189728214-319cb5d0-a55d-4726-8b62-1c0170115f09.png)

### Edit existing games
All attributes of a game can be changed here. This is also where games can be deleted from the list

![Screenshot from 2022-09-12 19-12-28](https://user-images.githubusercontent.com/101006560/189728737-54c50d77-3204-40c1-b16c-ceafef7ae490.png)

### Add new consoles
The list is intented to be used over a long period of time, so naturally new consoles will pop up along the way. Adding, deleting and even updating console names is also done within the program

![Screenshot from 2022-09-12 19-12-53](https://user-images.githubusercontent.com/101006560/189729087-50a66525-c6ba-42a0-983f-10b1061dbe8b.png)

## Setup
### Requirements
- Python3 (I use 3.10)
- PyQt5
- Pandas

### Local files
GamesList uses three different files, `Games.txt`, `Status.txt` and `Consoles.txt`. All three will be created (with some default values) if they don't already exist. `Games.txt` and `Consoles.txt` are fine as-is and can be edited through the program, however you might want to take a look at `Status.txt` before using the program too much.

`Status.txt` is an ordered list of the different statuses you can assign to a game. It is generated with the statuses `Playing`, `To do`, `Consider`, `Done` and `Dropped` which I would consider as a pretty minimal set of statuses.

The statuses I currently use are
- `Playing`: Games I'm playing nowadays
- `Soon`: Games I want to start playing soon
- `To do`: Games I plan on playing sometime in the future
- `Consider`: Games that I might play at some point, but haven't decided
- `Whenever`: Games I can pick up and play at any time without much commitment (e.g. CS:GO or HoMM3)
- `Done`: Games I have beat or have made sufficient progress that I consider them "done"
- `Dropped`: Games I didn't want to finish

The statuses you want must be entered directly into the `Status.txt` file and I haven't implemented a neat way to reassign the status of a batch of games. If you need to rename statuses or add new ones, you'll have to open the `Games.txt` file and use find&replace (just be careful)
