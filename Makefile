# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: chrilomb <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/03/29 17:12:00 by chrilomb          #+#    #+#              #
#    Updated: 2026/03/29 17:17:51 by chrilomb         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

NAME = fly-in.py
FILE = .base

all: $(NAME)

$(NAME):
	@python3 $(NAME) $(FILE)

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict


