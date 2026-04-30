# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    dependency_check.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: chrilomb <chrilomb@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/03/29 17:01:13 by chrilomb          #+#    #+#              #
#    Updated: 2026/04/30 17:32:07 by chrilomb         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

def check_dependencies():
    try:
        import numpy
        import matplotlib
        import pandas
        import pygame
        return True
    except ImportError as e:
        print(f"Dependency error: {e}")
        return False
