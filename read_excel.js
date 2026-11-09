const xlsx = require('xlsx');
const fs = require('fs');

const wb = xlsx.readFile('C:/Users/tawfe/.gemini/antigravity/brain/c24f9ec1-3d40-425f-8100-d03f24cb1018/.user_uploaded/media_1794211825279_20e7111a.xlsx');
console.log('Sheets:', wb.SheetNames);

wb.SheetNames.forEach(sheetName => {
  const ws = wb.Sheets[sheetName];
  const data = xlsx.utils.sheet_to_json(ws, {header:1});
  console.log(`\n=== Sheet: ${sheetName} ===`);
  console.log('Headers:', JSON.stringify(data[0]));
  console.log('Row1:', JSON.stringify(data[1]));
  console.log('Row2:', JSON.stringify(data[2]));
  console.log('Row3:', JSON.stringify(data[3]));
  console.log('Total rows:', data.length);
  
  // Also export as JSON
  const jsonData = xlsx.utils.sheet_to_json(ws);
  fs.writeFileSync(`C:/Users/tawfe/Downloads/Hackathon/ProjectFolder/data_${sheetName}.json`, JSON.stringify(jsonData, null, 2));
  console.log(`Exported ${jsonData.length} records to data_${sheetName}.json`);
});

