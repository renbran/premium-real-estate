#!/usr/bin/env bash
# ===========================================================
# ONE-SHOT CLEAN-UP FOR  hr_employee_import_fix
# ===========================================================

set -e

CONF_FILE="/etc/odoo/odoo.conf"
DB="testerp"
MODULE="hr_employee_import_fix"
ODOO_USER="odoo"
SERVICE="odoo"
ADDONS_DIR="/var/odoo/testerp/addons"

echo "[*] Stopping Odoo..."
sudo systemctl stop "$SERVICE"

# -----------------------------------------------------------
# 1. Remove the addon directory
# -----------------------------------------------------------
if [ -d "$ADDONS_DIR/$MODULE" ]; then
    echo "[*] Removing $ADDONS_DIR/$MODULE..."
    rm -rf "$ADDONS_DIR/$MODULE"
else
    echo "[-] Directory $ADDONS_DIR/$MODULE already gone"
fi

# -----------------------------------------------------------
# 2. Uninstall the module inside the database
# -----------------------------------------------------------
echo "[*] Uninstalling module $MODULE from database $DB..."
sudo -u "$ODOO_USER" odoo shell -c "$CONF_FILE" -d "$DB" --no-http --log-level=error <<'PY'
import logging
from odoo import api, SUPERUSER_ID
_logger = logging.getLogger(__name__)
env = api.Environment(cr, SUPERUSER_ID, {})
mod = env['ir.module.module'].search([('name','=','hr_employee_import_fix')])
if mod:
    _logger.warning("Uninstalling %s", mod.name)
    mod.button_immediate_uninstall()
else:
    _logger.warning("Module %s not found in DB", 'hr_employee_import_fix')
PY

# -----------------------------------------------------------
# 3. Purge any remaining XML-IDs / obsolete data
# -----------------------------------------------------------
echo "[*] Cleaning orphaned metadata..."
sudo -u postgres psql "$DB" <<SQL
DELETE FROM ir_model_data WHERE module = 'hr_employee_import_fix';
DELETE FROM ir_ui_view v
USING ir_model_data d
WHERE d.model='ir.ui.view'
  AND d.res_id = v.id
  AND d.module = 'hr_employee_import_fix';
SQL

# -----------------------------------------------------------
# 4. Restart Odoo
# -----------------------------------------------------------
echo "[*] Starting Odoo..."
sudo systemctl start "$SERVICE"
