#!/bin/bash
# ═══════════════════════════════════════════════════════════
# NEXUS - Détecteur de doublons (Mode lecture seule)
# Scanne récursivement et détecte les fichiers identiques
# ═══════════════════════════════════════════════════════════

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

SCAN_DIR="${1:-.}"  # Dossier à scanner (défaut: current)
REPORT_FILE="rapport_doublons_$(date +%Y%m%d_%H%M%S).txt"
TEMP_HASHES="/tmp/nexus_hashes_$$.txt"

# Extensions à scanner (ajuste selon besoins)
EXTENSIONS=("pdf" "docx" "doc" "txt" "md" "pptx" "xlsx" "zip" "rar" "jpg" "png")

# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════

print_header() {
    echo -e "${CYAN}"
    echo "═══════════════════════════════════════════════════════════"
    echo "  🔍 NEXUS - DÉTECTEUR DE DOUBLONS"
    echo "═══════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

print_config() {
    echo -e "${BLUE}📂 Dossier scanné:${NC} $SCAN_DIR"
    echo -e "${BLUE}📄 Rapport:${NC} $REPORT_FILE"
    echo -e "${BLUE}📋 Extensions:${NC} ${EXTENSIONS[*]}"
    echo ""
}

build_find_pattern() {
    # Construit le pattern pour find
    local pattern=""
    for ext in "${EXTENSIONS[@]}"; do
        if [ -z "$pattern" ]; then
            pattern="-iname *.${ext}"
        else
            pattern="$pattern -o -iname *.${ext}"
        fi
    done
    echo "$pattern"
}

scan_files() {
    echo -e "${YELLOW}🔍 Scan des fichiers en cours...${NC}"

    # Trouve tous les fichiers avec extensions
    local find_pattern=$(build_find_pattern)
    local total_files=$(eval "find \"$SCAN_DIR\" -type f \( $find_pattern \)" | wc -l)

    echo -e "${GREEN}✅ $total_files fichiers trouvés${NC}"
    echo ""

    # Calcule les hash MD5
    echo -e "${YELLOW}🔐 Calcul des empreintes MD5...${NC}"

    > "$TEMP_HASHES"  # Vide le fichier temp

    local count=0
    eval "find \"$SCAN_DIR\" -type f \( $find_pattern \)" | while IFS= read -r file; do
        count=$((count + 1))

        # Progress bar
        if [ $((count % 10)) -eq 0 ]; then
            echo -ne "\r⏳ Progression: $count / $total_files"
        fi

        # Calcule MD5
        if command -v md5sum &> /dev/null; then
            hash=$(md5sum "$file" | awk '{print $1}')
        elif command -v md5 &> /dev/null; then
            hash=$(md5 -q "$file")
        else
            echo -e "${RED}❌ Erreur: md5sum ou md5 non trouvé${NC}"
            exit 1
        fi

        # Stocke: HASH|FICHIER
        echo "$hash|$file" >> "$TEMP_HASHES"
    done

    echo -e "\n${GREEN}✅ Calcul terminé${NC}\n"
}

detect_duplicates() {
    echo -e "${YELLOW}🔎 Détection des doublons...${NC}"

    # Initialise rapport
    {
        echo "═══════════════════════════════════════════════════════════"
        echo "  RAPPORT DE DÉTECTION DES DOUBLONS"
        echo "  Date: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "  Dossier scanné: $SCAN_DIR"
        echo "═══════════════════════════════════════════════════════════"
        echo ""
    } > "$REPORT_FILE"

    # Trouve les doublons (hashes qui apparaissent > 1 fois)
    local duplicate_hashes=$(awk -F'|' '{print $1}' "$TEMP_HASHES" | sort | uniq -d)

    if [ -z "$duplicate_hashes" ]; then
        echo -e "${GREEN}✅ Aucun doublon détecté !${NC}"
        {
            echo "✅ RÉSULTAT: Aucun doublon trouvé"
            echo ""
            echo "Tous les fichiers sont uniques."
        } >> "$REPORT_FILE"
        return
    fi

    # Compte total de doublons
    local duplicate_count=0
    local group_count=0

    echo "$duplicate_hashes" | while IFS= read -r hash; do
        group_count=$((group_count + 1))

        # Trouve tous les fichiers avec ce hash
        local files=$(grep "^$hash|" "$TEMP_HASHES" | cut -d'|' -f2)
        local file_count=$(echo "$files" | wc -l)
        duplicate_count=$((duplicate_count + file_count - 1))  # -1 car on garde l'original

        {
            echo "════════════════════════════════════════════════════════"
            echo "🔴 GROUPE DE DOUBLONS #$group_count"
            echo "════════════════════════════════════════════════════════"
            echo "Hash MD5: $hash"
            echo "Nombre de copies: $file_count"
            echo ""
            echo "Fichiers identiques:"
            echo "$files" | nl -w2 -s'. '
            echo ""

            # Taille du fichier
            local first_file=$(echo "$files" | head -n1)
            if [ -f "$first_file" ]; then
                local size=$(du -h "$first_file" | cut -f1)
                echo "Taille: $size"
                echo "Espace gaspillé: $size × $(($file_count - 1)) copies"
            fi
            echo ""
        } >> "$REPORT_FILE"
    done

    # Résumé
    local total_duplicate_count=$(echo "$duplicate_hashes" | wc -l)

    {
        echo "═══════════════════════════════════════════════════════════"
        echo "  RÉSUMÉ"
        echo "═══════════════════════════════════════════════════════════"
        echo "📊 Groupes de doublons: $total_duplicate_count"
        echo "📄 Fichiers en double: À calculer manuellement"
        echo ""
        echo "💡 ACTIONS RECOMMANDÉES:"
        echo "   1. Vérifie chaque groupe"
        echo "   2. Garde la version la plus récente ou la mieux nommée"
        echo "   3. Utilise le script de suppression si nécessaire"
        echo ""
        echo "⚠️  Ce rapport est en lecture seule"
        echo "   Aucun fichier n'a été modifié ou supprimé"
    } >> "$REPORT_FILE"

    echo -e "${RED}⚠️  $total_duplicate_count groupes de doublons trouvés${NC}"
}

display_summary() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ SCAN TERMINÉ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}📄 Rapport détaillé:${NC} $REPORT_FILE"
    echo ""
    echo -e "${YELLOW}💡 Pour voir le rapport:${NC}"
    echo -e "   cat $REPORT_FILE"
    echo ""
    echo -e "${YELLOW}💡 Pour supprimer les doublons:${NC}"
    echo -e "   Utilise le script: ./supprimer_doublons.sh"
    echo ""
}

cleanup() {
    # Nettoie fichiers temporaires
    rm -f "$TEMP_HASHES"
}

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

trap cleanup EXIT

print_header
print_config

# Vérifie que le dossier existe
if [ ! -d "$SCAN_DIR" ]; then
    echo -e "${RED}❌ Erreur: Le dossier '$SCAN_DIR' n'existe pas${NC}"
    exit 1
fi

scan_files
detect_duplicates
display_summary

echo -e "${GREEN}🎉 Terminé !${NC}"
