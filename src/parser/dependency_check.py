# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    dependency_check.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: chrilomb <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/03/29 17:01:13 by chrilomb          #+#    #+#              #
#    Updated: 2026/03/29 17:01:42 by chrilomb         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

def check_dependencies():
    try:
        import numpy
        import matplotlib
        import pandas
        return True
    except ImportError as e:
        print(f"Dependency error: {e}")
        return False
