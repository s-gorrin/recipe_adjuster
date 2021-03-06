"""
Purpose:
    to scale the size of a recipe based
    on a different quantity of a single ingredient

Algorithm:
    ratio = (new amount / old amount)
    multiply each ingredient by ratio

Process:
    read recipe from user prompted filename
    ask user input for ingredient to change
    find quantity of ingredient and calculate ratio
    multiply every quantity by ratio
    generate new file "filename_updated" for recipe
    print new recipe

Recipe format:
    this code will assume that recipes are formatted
    in the way that I always format recipes when I
    write them down.
    it expects a text file with one ingredient
    per line, in the following format:
        [number][unit][whitespace][ingredient]
    for example:
        256g    rice
        1024ml  water
    any method or instructions are expected to be at the end

Bread:
    work in progress. idea was to generate breasd recipes from
    amounts of ingrients, based on baker's percentage. currently
    not well integrated.
"""

import os


class Entry(object):
    """
    Object: storage container for each line of recipe
        with methods to print line, and to make line writable to a file.
    """
    def __init__(self, num, unit, ingr):
        self.num = num
        self.unit = unit
        self.ingr = ingr

    def print_out(self):
        if int(self.num) == self.num:
            number = int(self.num)
        else:
            number = self.num
        print(str(number) + self.unit + '\t' + self.ingr)

    def __repr__(self):
        return str(self.num) + self.unit + '\t' + self.ingr + '\n'


def parse_line(line):
    """
    Input: a 'line' from a recipe

    Returns a class Entry of the elements of that line:
        num - the quantity of the thing
        unit - the unit the thing is in
        ingr - the ingredient
    """
    num = ''
    unit = ''
    ingr = ''
    num_done = False
    if line[0].isnumeric():
        for c in line:
            if c.isnumeric() and not num_done:
                num += c
            elif c == '.':
                num += c
            else:
                num_done = True
                ingr += c
        try:
            unit = ingr[:ingr.index('\t')]
            ingr = ingr[(ingr.index('\t') + 1):-1]
            item = Entry(float(num), unit, ingr)
        except ValueError:
            return None
        return item
    else:
        return None


def manage_change(recipe):
    """
    Input: the recipe so far

    Takes user input and determines if it is in the recipe.

    Returns the ingredient to be changed
    """
    if len(recipe) == 0:
        print("I can't understand that recipe.")
        quit()
    change = input("What ingredient would you like to change?\n> ")
    while True:
        partials = []
        for item in recipe:
            if item.ingr == change:
                return change
            elif change in item.ingr:
                partials.append(item.ingr)
        if partials == []:
            change = \
                input("That item is not in the list, please try again.\n> ")
        elif len(partials) == 1:
            return partials[0]
        else:
            change = input("Did you mean one of these? "
                "Please type the full name:\n" + ", ".join(partials) + "\n> ")


def get_ratio(recipe):
    """
    Input: recipe list

    Returns the ratio by which each ingredient is changed.
    """
# Prompt ingredient to change, and by how much.
    change = manage_change(recipe)
    raw_adjust = input("How much of it do you have?\n> ")
    adjust = ''
    for c in raw_adjust:
        if c.isnumeric() or c == '.':
            adjust += c
    adjust = float(adjust)
# Finds the ratio of adjustment. If none is found, 1 is used.
    ratio = 1
    for item in recipe:
        if item.ingr == change:
            ratio = adjust / item.num
            break
    return ratio


def get_file():
    """
    Takes user input and finds the name of the recipe file.

    Returns a filename of a file that exists, from user input.
    """
    file_list = []
    for f in os.listdir():
        if f[-4:] == ".txt" or "." not in f:
            file_list.append(f)
    print(", ".join(file_list))
    while True:
        partials = []
        name = input("What is the name of the file?\n> ")
        exists = os.path.isfile(name)
        if exists:
            return name
        else:
            for f in file_list:
                if name in f:
                    partials.append(f)
        if partials == []:
            print("That does not appear to be a recipe, please try again.")
        elif len(partials) == 1:
            return partials[0]
        else:
            print("Did you mean one of these?\n" + ', '.join(partials))


def g_or_p(test):
    """
    Looks for '%' or 'g' in a test string.

    Returns the number as a decimal for percentages or alone if not.
    Returns None for errors or anything else
    """
    number = test.split(' ')[0]
    try:
        float(number)
        if '%' in test or "percent" in test:
            return round((float(number) / 100), 3)
        elif 'g' in test:
            return round(float(number), 1)
        else:
            return None
    except ValueError:
        return None


def bread():
    """
    Builds a bread recipe. Steps:

    Prompt number of loaves (a loaf is about 880g)
    List flours, by grams or percentage of each, based on a total
        Numbered list, pick by number
    Hydration percentage or grams
        (starting with 346g/loaf, maybe adjust for flour types)
    Default 9g salt per loaf
    Default 92g starter per loaf

    Generate file for finished recipe.

    This is not quite finished, but it mostly works. Current problem:
        there is a "close" for the recipe file, but bread never opens it.
        solution is probably a flag.
    """
    flour_menu = ["0: all purpose", "1: bread", "2: whole wheat", 
            "3: oat", "4: rye", "5: spelt", "6: barley"]
    print("\n".join(flour_menu), "\npick up to three by number")
    flour_list = []
    for i in range(3): # make list of flours in recipe
        flour = input("select a flour type or finish with flours\n> ")
        if flour.isnumeric() and int(flour) in range(7):
            flour_list.append(flour_menu[int(flour)])
        else:
            break
    bread_recipe = []
    total_flour = 0
    for item in flour_list: # generate Entry for flours
        test = input("how much " + item + "? (format: \"x g\" or \"y %\")\n> ")
        amount = g_or_p(test)
        if amount < 1:
            bread_recipe.append(Entry((amount * 433.5), 'g', item))
            total_flour += (amount * 433.5)
        else:
            bread_recipe.append(Entry(amount, 'g', item))
            total_flour += amount
    water = input("what percent hydration?"
            "(just a number, if unsure, \"80\")\n> ")
    bread_recipe.append(Entry(((float(water) / 100) * total_flour),
        'g', "water"))
    salt = input("how much salt? (just a number in grams. if unsure, \"9\"\n> ")
    bread_recipe.append(Entry(float(salt), 'g', "salt"))
    bread_recipe.append(Entry(92, 'g', "starter"))
    return bread_recipe


recipe = []  # The list of recipe elements
method = ''  # Everything thing in the file that is not ingredients
"""
files = get_files()
print(", ".join(files))
filename = input("What is the name of the file?\n> ")
"""

# Bread prompt goes here
if input("are you making bread? (y/n)\n> ") == 'y':
    recipe = bread()
    filename = "bread_recipe.txt"
else:
# Take open, read, parse recipe.
    filename = get_file()
    file_in = open(filename, 'r')
    for line in file_in:
        parsed = parse_line(line)
        if parsed:
            recipe.append(parsed)
        else:
            method += line
    for item in recipe:
        item.print_out()

ratio = get_ratio(recipe)

# Adjust recipe, print adjusted recipe, write to a new file
adjusted_recipe = open("adjusted_" + filename, 'w')
for item in recipe:
    item.num = round(item.num * ratio, 1)
    if int(item.num * 10) % 10 == 0:
        item.num = int(item.num)
    adjusted_recipe.write(repr(item))
    item.print_out()  # Print finished recipe to the console

adjusted_recipe.write(method)  # Write method to output file
print(method)

file_in.close()
adjusted_recipe.close()
