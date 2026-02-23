#!/bin/bash
# ═══════════════════════════════════════════════════════════
# NEXUS - Suppresseur de doublons (Mode interactif)
# Supprime les fichiers doublons avec confirmation
# ═══════════════════════════════════════════════════════════

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

SCAN_DIR="${1:-.}"
BACKUP_DIR="backup_doublons_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="suppression_log_$(date +%Y%m%d_%H%M%S).txt"
TEMP_HASHES="/tmp/nexus_hashes_delete_$$.txt"
DELETED_COUNT=0
SPACE_SAVED=0

# Mode
AUTO_MODE="${2:-interactive}"  # interactive ou auto

# Extensions
EXTENSIONS=("pdf" "docx" "doc" "txt" "md" "pptx" "xlsx" "zip" "rar" "jpg" "png")

# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════

print_header() {
    echo -e "${RED}"
    echo "═══════════════════════════════════════════════════════════"
    echo "  🗑️  NEXUS - SUPPRESSEUR DE DOUBLONS"
    echo "  ⚠️  MODE: ${AUTO_MODE^^}"
    echo "═══════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

print_warning() {
    echo -e "${YELLOW}"
    echo "⚠️  ATTENTION ⚠️"
    echo ""
    echo "Ce script va supprimer des fichiers !"
    echo ""
    echo "Recommandations:"
    echo "  1. ✅ Lance d'abord le script de détection"
    echo "  2. ✅ Vérifie que tu as des backups"
    echo "  3. ✅ Un backup automatique sera créé dans: $BACKUP_DIR"
    echo ""
    echo -e "${NC}"

    if [ "$AUTO_MODE" != "auto" ]; then
        read -p "Continuer ? (oui/non): " confirm
        if [ "$confirm" != "oui" ]; then
            echo -e "${GREEN}Annulé par l'utilisateur${NC}"
            exit 0
        fi
    fi
}

build_find_pattern() {
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

scan_and_hash() {
    echo -e "${YELLOW}🔍 Scan des fichiers...${NC}"

    local find_pattern=$(build_find_pattern)
    local total_files=$(eval "find \"$SCAN_DIR\" -type f \( $find_pattern \)" | wc -l)

    echo -e "${GREEN}✅ $total_files fichiers trouvés${NC}"

    echo -e "${YELLOW}🔐 Calcul des empreintes MD5...${NC}"

    > "$TEMP_HASHES"

    local count=0
    eval "find \"$SCAN_DIR\" -type f \( $find_pattern \)" | while IFS= read -r file; do
        count=$((count + 1))

        if [ $((count % 10)) -eq 0 ]; then
            echo -ne "\r⏳ Progression: $count / $total_files"
        fi

        if command -v md5sum &> /dev/null; then
            hash=$(md5sum "$file" | awk '{print $1}')
        elif command -v md5 &> /dev/null; then
            hash=$(md5 -q "$file")
        else
            echo -e "${RED}❌ md5sum ou md5 requis${NC}"
            exit 1
        fi

        # Stocke: HASH|TAILLE|MTIME|FICHIER
        local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file")
        local mtime=$(stat -f%m "$file" 2>/dev/null || stat -c%Y "$file")
        echo "$hash|$size|$mtime|$file" >> "$TEMP_HASHES"
    done

    echo -e "\n${GREEN}✅ Scan terminé${NC}\n"
}

process_duplicates() {
    echo -e "${YELLOW}🔎 Traitement des doublons...${NC}\n"

    # Crée backup dir
    mkdir -p "$BACKUP_DIR"

    # Log header
    {
        echo "═══════════════════════════════════════════════════════════"
        echo "  LOG DE SUPPRESSION DES DOUBLONS"
        echo "  Date: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "  Mode: $AUTO_MODE"
        echo "═══════════════════════════════════════════════════════════"
        echo ""
    } > "$LOG_FILE"

    # Trouve hashes dupliqués
    local duplicate_hashes=$(awk -F'|' '{print $1}' "$TEMP_HASHES" | sort | uniq -d)

    if [ -z "$duplicate_hashes" ]; then
        echo -e "${GREEN}✅ Aucun doublon à supprimer !${NC}"
        return
    fi

    local group_num=0

    echo "$duplicate_hashes" | while IFS= read -r hash; do
        group_num=$((group_num + 1))

        echo -e "${CYAN}════════════════════════════════════════${NC}"
        echo -e "${CYAN}📦 GROUPE #$group_num${NC}"
        echo -e "${CYAN}════════════════════════════════════════${NC}"

        # Récupère tous les fichiers avec ce hash
        local files_data=$(grep "^$hash|" "$TEMP_HASHES")

        # Trie par date (plus récent en premier)
        local sorted_files=$(echo "$files_data" | sort -t'|' -k3 -rn)

        # Sépare le fichier à garder (le plus récent) et les doublons
        local keep_file=$(echo "$sorted_files" | head -n1 | cut -d'|' -f4)
        local duplicate_files=$(echo "$sorted_files" | tail -n +2 | cut -d'|' -f4)

        echo -e "${GREEN}✅ À GARDER (plus récent):${NC}"
        echo "   $keep_file"
        echo ""

        echo -e "${RED}❌ DOUBLONS (à supprimer):${NC}"
        echo "$duplicate_files" | nl -w2 -s'. '
        echo ""

        # Log
        {
            echo "════════════════════════════════════════════════════════"
            echo "GROUPE #$group_num - Hash: $hash"
            echo "════════════════════════════════════════════════════════"
            echo "GARDÉ: $keep_file"
            echo ""
            echo "SUPPRIMÉS:"
        } >> "$LOG_FILE"

        # Demande confirmation ou auto
        local should_delete="yes"
        if [ "$AUTO_MODE" != "auto" ]; then
            read -p "Supprimer ces doublons ? (oui/non/skip): " action
            should_delete="$action"
        fi

        if [ "$should_delete" = "oui" ] || [ "$should_delete" = "yes" ]; then
            echo "$duplicate_files" | while IFS= read -r dup_file; do
                if [ -f "$dup_file" ]; then
                    # Backup avant suppression
                    local backup_path="$BACKUP_DIR/$(basename "$dup_file")"
                    cp "$dup_file" "$backup_path" 2>/dev/null || true

                    # Taille pour stats
                    local file_size=$(stat -f%z "$dup_file" 2>/dev/null || stat -c%s "$dup_file")
                    SPACE_SAVED=$((SPACE_SAVED + file_size))

                    # Supprime
                    rm -f "$dup_file"
                    DELETED_COUNT=$((DELETED_COUNT + 1))

                    echo -e "   ${RED}🗑️  Supprimé:${NC} $(basename "$dup_file")"
                    echo "   - $dup_file" >> "$LOG_FILE"
                fi
            done
            echo "" >> "$LOG_FILE"
        else
            echo -e "${YELLOW}⏭️  Groupe ignoré${NC}"
            echo "IGNORÉ (par utilisateur)" >> "$LOG_FILE"
            echo "" >> "$LOG_FILE"
        fi

        echo ""
    done
}

display_summary() {
    # Convertit bytes en human readable
    local space_mb=$((SPACE_SAVED / 1024 / 1024))
    local space_gb=$(echo "scale=2; $SPACE_SAVED / 1024 / 1024 / 1024" | bc)

    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ SUPPRESSION TERMINÉE${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}📊 STATISTIQUES:${NC}"
    echo -e "   🗑️  Fichiers supprimés: ${RED}$DELETED_COUNT${NC}"
    echo -e "   💾 Espace libéré: ${GREEN}${space_mb} MB ($space_gb GB)${NC}"
    echo ""
    echo -e "${BLUE}💾 BACKUP:${NC} $BACKUP_DIR"
    echo -e "${BLUE}📄 LOG:${NC} $LOG_FILE"
    echo ""

    if [ $DELETED_COUNT -gt 0 ]; then
        echo -e "${YELLOW}💡 Les fichiers supprimés sont dans le backup${NC}"
        echo -e "${YELLOW}   Pour restaurer: cp $BACKUP_DIR/* /destination/${NC}"
    fi
    echo ""

    # Log summary
    {
        echo "═══════════════════════════════════════════════════════════"
        echo "  RÉSUMÉ"
        echo "═══════════════════════════════════════════════════════════"
        echo "Fichiers supprimés: $DELETED_COUNT"
        echo "Espace libéré: $space_mb MB ($space_gb GB)"
        echo "Backup: $BACKUP_DIR"
    } >> "$LOG_FILE"
}

cleanup() {
    rm -f "$TEMP_HASHES"
}

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

trap cleanup EXIT

print_header

# Vérifie dossier
if [ ! -d "$SCAN_DIR" ]; then
    echo -e "${RED}❌ Erreur: '$SCAN_DIR' n'existe pas${NC}"
    exit 1
fi

print_warning

echo -e "${BLUE}📂 Dossier:${NC} $SCAN_DIR"
echo -e "${BLUE}💾 Backup:${NC} $BACKUP_DIR"
echo ""

scan_and_hash
process_duplicates
display_summary

echo -e "${GREEN}🎉 Terminé !${NC}"
