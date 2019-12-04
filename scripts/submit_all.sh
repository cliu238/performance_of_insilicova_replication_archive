SUBMIT_SCRIPT=$(dirname $0)/submit_analysis.sh
SPLITS=500


$SUBMIT_SCRIPT validate $SPLITS tariff phmrc
$SUBMIT_SCRIPT validate $SPLITS insilico insilico
$SUBMIT_SCRIPT default $SPLITS insilico insilico

$SUBMIT_SCRIPT validate $SPLITS tariff phmrc 1
$SUBMIT_SCRIPT validate $SPLITS insilico insilico 1
$SUBMIT_SCRIPT default $SPLITS insilico insilico 1
