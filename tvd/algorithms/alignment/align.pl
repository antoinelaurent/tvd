#!/usr/bin/perl

if(scalar(@ARGV) != 3){
	die "Usage : $0 fichierTxt(Node1-Node2#Speaker#text) fichierAudio name\n";
}

$txt = $ARGV[0];
$wav = $ARGV[1];
$name = $ARGV[2];

%map = ();
$map{"‘"}="'";
$map{"…"}="...";
$map{"–"}="-";
$map{"’"}="'";


open(OUT, ">/tmp/$name.txt");
open(TXT, $txt);
while($ligneC = <TXT>){
	chomp($ligneC);
	if($ligneC =~ /^[^#]+#[^#]+#(.*)/){
		$ligne = $1;
		print OUT nettoyerLigne($ligne)."\n";	
	}
}
close(TXT);
close(OUT);


$cmd = "cat /tmp/$name.txt | utf2iso 2> /tmp/$name.txt.iso.error 1> /dev/null";
system($cmd);

if(-s "/tmp/$name.txt.iso.error" > 0){
	die "Error during conversion ... see /tmp/$name.txt.iso.error"
}
unlink "/tmp/$name.txt.iso.error";

$cmd = "mkdir align";
system($cmd) if(!-d "align");

$cmd = "vrbs_align -l:eng -v -f $wav /tmp/$name.txt > align/$name.xml";
system($cmd) if(!-e "align/$name.xml");


$cmd = "cat align/$name.xml | xml2ctm > /tmp/text.ctm";
system($cmd);

$ficDump = $txt;
$ficCTM = "/tmp/text.ctm";

$cmd = "cat $ficCTM";
@ctm = `$cmd`;

$indCtm = 0;

open(FIC, $ficDump);
while($ligne = <FIC>){
	chomp($ligne);
	
	@infos = split(/#/, $ligne);
	$nodes = $infos[0];
	$spk = $infos[1];

	$spk =~ s/ +/_/g;

	$txt = $infos[2];
	
	$txt = nettoyerLigne($txt);
	$txt = trim($txt);

	#$txt =~ s/([^\.])\./$1 \./g;
	#$txt =~ s/([^\,])\,/$1 \,/g;
	#$txt =~ s/([^\?])\?/$1 \?/g;
	#$txt =~ s/([^\!])\!/$1 \!/g;

	@words = split(/ +/, $txt);

	foreach(@words){
		$word = $_;
		$original = $word;
		$end = 0;
		while(!$end){
			$ctmL = $ctm[$indCtm];
			@iCtm = split(/ /, $ctmL);
			$wCtm = $iCtm[4];
			$wCtm = virerPonctuation($wCtm);
			if($wCtm ne ""){
				$end=1;
			}else{
				$indCtm++;
			}
			$end = 1 if($indCtm == scalar(@ctm));
		}

		
		$word = virerPonctuation($word);	

		@iCtm = split(/ /, $ctmL);
		$show = $iCtm[0];
		$start = $iCtm[2];
		$duree = $iCtm[3];
		$score = $iCtm[5];
		$end = sprintf("%.3f", $start+$duree);

		$wCtm = $iCtm[4];
		$wCtm = virerPonctuation($wCtm);	
		

		if($word ne ""){
			
			if($word eq $wCtm){
				print "thrones_s01e01 $nodes $spk $original ($start - $end - $score)\n";
			}else{
				die "==> ". $word . " ne ".$wCtm."\n";
				
			}

			$indCtm++;
		}else{
			print "thrones_s01e01 $nodes $spk $original\n" if($original ne "");
		}
	}

	
	
}
close(FIC);
	
clean();

sub clean{
	unlink "/tmp/$name.txt";
	unlink "/tmp/text.ctm";
}


sub virerPonctuation{
	my $word = $_[0];
	$word =~ s/,//g;
    $word =~ s/\.//g;       
    $word =~ s/\?//g;       
    $word =~ s/\!//g;
	$word =~ s/\"//g;    
	$word =~ s/\://g;
	$word =~ s/\;//g;
	return trim($word);
}

sub trim{
        $chaine = $_[0];
        $chaine =~ s/^\s+//g;
        $chaine =~ s/\s+$//g;
        return $chaine;
}
sub nettoyerLigne{
        my $ligne=$_[0];
        foreach(keys %map){
                $ligne =~ s/$_/$map{$_}/g;
        }
        $ligne =~ s/\.\.\.([^\.])/\.\.\. $1/g;
        $ligne =~ s/ +/ /g;
        $ligne =~ s/\([^\)]+\)//g;
        $ligne =~ s/\[[^\]]+\]//g;
        return $ligne;
}
