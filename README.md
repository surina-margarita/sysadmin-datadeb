# sysadmin-datadeb

## Exercice

* **Partie 1** : Créer un paquet Debian contenant un script Python affichant la date et l’heure dans trois fuseaux horaires (local, GMT, Tuvalu).
* **Partie 2** : Mettre en place un miroir trivial en HTTP local.
* **Partie 3** : Signer les paquets.

---

## Partie 1 — Création du paquet Debian

### 1. Rédiger le script Python

Créer un script nommé `affiche_date.py` qui :

* Affiche la date et l’heure locales,
* Affiche l’heure en GMT,
* Affiche l’heure dans le fuseau horaire de Tuvalu (Pacific/Funafuti).

Utiliser les modules `datetime` et `zoneinfo`, fournis par les paquets Debian (`python3`, `tzdata`).

Enregistrer le script dans `/lib/affiche_date.py` et le rendre exécutable :

```bash
sudo chmod +x /lib/affiche_date.py
```

### 2. Préparer l’arborescence du paquet

Créer la structure du paquet Debian :

```bash
mkdir -p monpaquet_deb/DEBIAN
mkdir -p monpaquet_deb/lib
```

Copier le script `affiche_date.py` dans `monpaquet_deb/lib/`.

### 3. Définir les métadonnées du paquet

Créer le fichier `monpaquet_deb/DEBIAN/control` avec le contenu suivant :

```
Package: affiche-date-margosurina
Version: 1.0
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-tz, tzdata
Maintainer: Margo Surina
Description: Afficher la date et l'heure dans différents fuseaux horaires.
```

### 4. Ajouter un script post-installation (`postinst`)

Créer le fichier `monpaquet_deb/DEBIAN/postinst` avec les instructions suivantes :

```bash
#!/bin/bash
ln -sf /lib/affiche_date.py /usr/bin/affiche_date
chmod +x /usr/bin/affiche_date
```

Rendre le script exécutable :

```bash
chmod +x monpaquet_deb/DEBIAN/postinst
```

#### À propos de `postinst`

Le script `postinst` est un script exécuté automatiquement après l’installation du paquet via `dpkg`.
Dans ce cas, il crée un lien symbolique dans `/usr/bin` pointant vers le script Python installé dans `/lib/`. Cela permet d’exécuter le programme directement depuis la ligne de commande, sans spécifier son chemin complet.

### 5. Construire le paquet

Utiliser `dpkg-deb` pour générer le fichier `.deb` :

```bash
dpkg-deb --build monpaquet_deb
```

Le fichier `monpaquet_deb.deb` est ainsi produit.

### 6. Installer et tester le paquet

Installer le paquet :

```bash
sudo dpkg -i monpaquet_deb.deb
```

Vérifier la présence du lien symbolique :

```bash
ls -l /usr/bin/affiche_date
```

Exécuter le script via le lien :

```bash
affiche_date
```

Le script affiche la date et l’heure dans les trois fuseaux.

Tester la désinstallation :

```bash
sudo apt remove affiche-date-margosurina
```

S’assurer que le lien `/usr/bin/affiche_date` a bien été supprimé.


## Partie 2 — Mettre en place un miroir Debian local (HTTP)

### 1. Créer l’arborescence du dépôt

Créer la structure attendue par un dépôt Debian, en plaçant le fichier `.deb` dans un sous-dossier `pool/` :

```bash
sudo mkdir -p /var/www/html/deb/pool
sudo cp monpaquet_deb.deb /var/www/html/deb/pool/
```

### 2. Générer les fichiers d’index Debian

Se placer dans le répertoire `/var/www/html/deb/pool` et créer les fichiers requis pour que `apt` puisse lire le contenu du dépôt.

```bash
cd /var/www/html/deb/pool
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz
apt-ftparchive release . > Release
```

### 3. Servir le dépôt via un serveur HTTP

Utiliser un serveur web local tel qu’Apache ou NGINX pour exposer le répertoire `/var/www/html/deb` via HTTP. Pour cet exercice, j'ai utilisé un serveur Apache.

### 4. Ajouter le miroir local à `apt`

Créer un fichier  dans `/etc/apt/sources.list.d/` avec ce contenu :

```bash
deb [trusted=yes] http://localhost/deb ./
```

L’option `[trusted=yes]` permet d’éviter les avertissements liés à l’absence de signature.

### 5. Mettre à jour les sources et installer le paquet

Mettre à jour les métadonnées APT :

```bash
sudo apt update
```

Installer le paquet via le miroir :

```bash
sudo apt install affiche-date-margosurina
```

Exécuter le script pour vérification :

```bash
affiche-date-margosurina
```

## Partie 3 — Signer le dépôt Debian

### 1. Générer une paire de clés GPG

Utiliser `gpg` pour créer une nouvelle clé GPG :

```bash
gpg --full-generate-key
```

Suivre les instructions pour choisir :

* un type de clé RSA,
* une taille (par exemple 4096 bits),
* une date d’expiration,
* un nom et une adresse e-mail (utiliser un identifiant facilement reconnaissable, comme `clegpg`).

### 2. Exporter la clé publique

Exporter la clé publique au format ASCII-armored et la rendre accessible aux clients APT :

```bash
gpg --armor --export "clegpg" > public.key
sudo cp public.key /var/www/html/deb/
```

Cette clé sera utilisée côté client pour vérifier les signatures du dépôt.

### 3. Signer les métadonnées du dépôt

Se placer dans le répertoire contenant les fichiers du dépôt :

```bash
cd /var/www/html/deb
```

Signer le fichier `Release` de deux manières :

- En créant un fichier signé en clair (InRelease) :

  ```bash
  gpg --clearsign -o InRelease Release
  ```

- En créant une signature détachée :

  ```bash
  gpg -abs -o Release.gpg Release
  ```

Ces deux fichiers sont utilisés par APT pour valider l’origine et l’intégrité du dépôt.

### 4. Ajouter la clé au système client

Sur le poste client, ajouter la clé publique pour qu’APT puisse vérifier les signatures :

```bash
sudo apt-key add public.key
```

> Remarque : `apt-key` est obsolète mais encore fonctionnel. Pour une méthode plus conforme, utiliser `/etc/apt/trusted.gpg.d/` avec `gpg --dearmor`.

### 5. Ajouter le dépôt signé dans APT

Créer ou modifier un fichier dans `/etc/apt/sources.list.d/` :

```bash
sudo nano /etc/apt/sources.list.d/miroir-local.list
```

Ajouter la ligne suivante (sans l’option `[trusted=yes]`, désormais inutile grâce à la signature) :

```
deb http://localhost/deb ./
```

### 6. Mettre à jour et installer

Mettre à jour les métadonnées avec vérification de la signature :

```bash
sudo apt update
```

Installer le paquet :

```bash
sudo apt install affiche-date-margosurina
```

---

### Pourquoi signer uniquement le fichier `Release` est suffisant

Signer directement chaque fichier `.deb` est possible mais rarement pratiqué dans les dépôts Debian. En pratique, il est suffisant de signer le fichier `Release`, car :

* Le fichier `Release` contient les **hashs (SHA256/SHA512)** de tous les fichiers du dépôt, notamment `Packages.gz` et les fichiers `.deb` du répertoire `pool/`.
* `apt` vérifie ces hashs automatiquement après avoir validé la signature de `Release`. Cela garantit que les paquets n'ont pas été modifiés depuis la génération du dépôt.
* Cette approche est conforme à la méthode utilisée par les dépôts officiels Debian/Ubuntu.

Ainsi, la signature de `Release` assure à la fois l’authenticité et l’intégrité des métadonnées et des paquets référencés, ce qui est suffisant pour une distribution sécurisée.


