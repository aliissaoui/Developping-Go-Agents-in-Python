############################################################################################## ##################################### PROJET IA - GO ########################################

Binome :
- Achraf BENTAHER - Ali ISSAOUI

Encadrants: - Laurent Simon - Michaël Clément

##############################################################################################

Projet: Réalisation d'un joueur IA du jeu du GO.
Dans ce projet on a implémenté un agent IA du jeu du GO en utilisant les techniques étudié dans le cours comme AlphaBeta, NegaMax, Iterative Deepening.

Pré-requis
You need :

python
numpy
json
Eventuellement multiprocessing si vous voulez tester le joueur qui l'utilise ( décrit juste après )
Lancement
Plusieurs commandes sont possible comme précisé dans l'énoncé du projet: - python3 localGame.py : lance une partie de myPlayer vs myPlyaer - python3 namedGame.py aPlayer bPlayer : lance une partie de aPlayer vs bPlayer

Les joueurs disponibles sont randomPlayer et myPlayer.

Les joueurs:
Nous avons d'abords plusieurs joueurs:

myPlayer.py : Le joueur principal utilisant AlphaBeta avec Iterative Deepening.
NGPlayer.py : Un joueur secondaire utilisant NegaMax avec Iterative Deepening.
abThreadedPlayer.py : Un joueur qui est hors la compétition, puisqu'il utilise un AlphaBeta avec multiprocessing.
L'ouverture: Pour l'ouverture ( la même pour les 3 joueurs ), nous avons utilisé le fichier games.json pour récupérer à chaque fois les meilleurs ouvertures.

Les fichiers:
 eval.py : Ce fichier contient la fonction d'évaluation utilisée dans les recherches, cette fonction est divisé en plusieurs goals:

              Goal1   : Maximisation du nombre des pions de mes couleurs.
              Goal2   : Maximisation de mon nombre de libertés.
              Goal3   : Eviter les bordures du board.
              Goal31  : On a utilisé la distance de Manhattan pour jouer le plus proche possible du centre du plateau.
              Goal4   : Maximiser le nombre des pions qu'on capture.
              Goal5   : Maximiser le nombre de mes pions connectés. ( Non utilisé avec goal6 )
              Goal6   : Minimiser le nombre d'Euler, le nombre d'Euler se calcule à partir de quelques patterns dans le plateau et en
                      le minimisant on maximise le nombre des pions connectés et des cercles crées
                      source : http://erikvanderwerf.tengen.nl/pubdown/thesis_erikvanderwerf.pdf?fbclid=IwAR0rfZGdM_cRz8mklnvqHKSCcrxOLwid1gAx0NXVO2bGk8_incl39vP-kv8 ( Page 52 )

              ces goals sont finalement multipliés par des coefficients et sommés pour donner une évaluation du plateau.
alphaBeta.py : Ce fichier contient l'implémentation de la fonction de recherche AlphaBeta avec une profondeur spécifiée dans myPlayer.py L'implémentation est plus ou moins classique, sauf qu'on ne considère pas les bordures ( 2 cases puis une seul ) pendant les premiers tours du jeu puisque notre joueur préfère commencer au milieu.

negaMax.py : Ce fichier contient l'implémentation de la fonction de recherche NegaMax ( se basant sur l'AlphaBeta précédent ) avec une profondeur spécifiée dans myPlayer.py

abThreadedPlayer.py : Malheureusement, on ne savait pas que l'utilisation du multiprocessing est interdite, on l'avait quand même
implémenté. Le principe étant de créer, dès la première itération de AlphaBetaCoup, un procéssus à chaque legal_move est de faire le calcul dans ce processus. Cette implémentation nous a beaucoup amélioré la vitesse des calculs, par exemple dans un petit teste on avait au début du jeu:

                                              Normal                          MultiProcessing
                              
                              Depth2  :         17s                                4s
                              Depth3  :         40s                                11s   
ids.py : Ce fichier continent l'implémentation de l'Iterative Deepening pour les 3 recherches précédents. Nous avons utiliser des signaux de type SIGALRM pour interempre la fonction de recherche avec un timeout une fois que le temps précisé dans le Xplayer.py est écoulé. L'implémentation de cette fonction à posé un problème avec la version Multiprocessing puisque le signal SIGALRM n'est envoyer qu'au processus courant, les autres processus restent donc actifs. On a trouvé une solution en sauvegardant les processus fils et les arrêtant avec termine() une fois que le temps est écoulé ( fonction IDS_AB_threaded dans ids.py )

Auteurs
Étudiants de ENSEIRB-Matmeca :

Ali ISSAOUI
Achraf Bentaher
Remerciements
Laurent Simon
Michaël Clément
