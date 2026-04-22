# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    file_parse.py                                      :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: chrilomb <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/03/29 17:03:49 by chrilomb          #+#    #+#              #
#    Updated: 2026/03/29 17:11:25 by chrilomb         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

def parse_file(file: TextIO) -> list:
    data = []
    for line in file:
        line = line.strip()
        if line and not line.startswith('#'):
            data.append(line)
    return data
