import subprocess
while True:
    print('---------------------------------------------------------')
    print('Menu de seleção de scripts:\n1 - getDepartments.py\n2 - getTeachers.py\n3 - getCourses.py\n4 - getClasses.py')
    print('---------------------------------------------------------')

    option = input("Digite o número: ")

    if option == '1':
        print('\nExecutando getDepartments.py:')
        subprocess.run(["python", "getDepartments.py"])
    elif option == '2':
        print('\nExecutando getTeachers.py:')
        subprocess.run(["python", "getTeachers.py"])
    elif option == '3':
        print('\nExecutando getCourses.py:')
        subprocess.run(["python", "getCourses.py"])
    elif option == '4':
        print('\nExecutando getClasses.py:')
        subprocess.run(["python", "getClasses.py"])
    else: print('Opção inválida.')

