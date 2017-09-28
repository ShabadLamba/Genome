function getListFromFirebase() {
	$.ajax({
		url: 'https://genome-3db7f.firebaseio.com/dna_features.json?shallow=true',
		type: 'GET',
		success: function(data) {
			console.log(data);
			var count = 0;
			genomes = [];
			for(i in data) {
				genomes.push({id: count, text: i});
				count++;	
			}
			console.log(genomes);
			$(".small_loader").css("display", "none");
			$(".selectGenome").css("display", "block");
			$(".js-example-data-array").select2({
			  data: genomes
			})
			getGenomeDataFromFirebase(genomes[0]["text"]);
		},
		error: function(err) {
			console.log(err);
		}
	})
}

function getGenomeDataFromFirebase(genome) {
	$("#loader").css("display", "block");
	$("#dataSection").css("display", "none");
	$.ajax({
		url: 'https://genome-3db7f.firebaseio.com/dna_features/' + genome + '.json',
		type: 'GET',
		success: function(data) {
			console.log(data);
			var dna = data.dna;
			var html = '';
			for(var i=0;i<data.sequenceList.length; i++) {
				html = html + '<tr>';
				html = html + '<td>' + data.sequenceList[i].promoter + '</td>';
				html = html + '<td>' + data.sequenceList[i].features.atgBox[0] + '</td>';
				html = html + '<td>' + data.sequenceList[i].features.tataBox[0] + '</td>';
				html = html + '<td>' + data.sequenceList[i].features.ttgacBox[0] + '</td>';
				html = html + '</tr>';
			}
			$(".selectedPhage").html(genome);
			$("#promoters").html(html);
			$(".dna").html("<span>" + dna + "</span>");
			$("#loader").css("display", "none");
			$("#dataSection").css("display", "block");
		},
		error: function(err) {
			console.log(err);
		}
	})
}

getListFromFirebase();

$(".js-example-data-array").on("select2:select", function(e) {
	console.log(e.params.data.text, e.params.data.id);
	getGenomeDataFromFirebase(e.params.data.text);
});