# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    main_parser.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: chrilomb <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/03/29 16:55:31 by chrilomb          #+#    #+#              #
#    Updated: 2026/03/29 17:11:25 by chrilomb         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from sys import argv
from dependency_check import check_dependencies

def main():
    if len(argv) != 2:
        raise ValueError("Usage: python fly_on.py <filename> or make")
    if check_dependencies() == False:
        raise ImportError("Missing dependencies. Please install them before running the program.")
    filename: str = argv[1]
    try:
        with open(filename, 'r') as file:
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    data: list[str] = parse_file(file)
    
